-- HedgeLab Database Schema
-- Run this script in your Supabase SQL editor to create the required tables

-- Enable Row Level Security (RLS) for all tables
-- You can customize the RLS policies based on your security requirements

-- Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

-- Opportunities Table
CREATE TABLE IF NOT EXISTS opportunities (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    signal_strength DECIMAL(5,3) NOT NULL,
    price DECIMAL(10,2),
    change_pct DECIMAL(8,3),
    volume BIGINT,
    date DATE NOT NULL,
    sector VARCHAR(100),
    potential_gain DECIMAL(8,3),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Positions Table
CREATE TABLE IF NOT EXISTS positions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    avg_cost DECIMAL(10,2) NOT NULL,
    pnl DECIMAL(15,2) DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio Performance Table
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_value DECIMAL(15,2) NOT NULL,
    returns DECIMAL(8,5),
    daily_return DECIMAL(8,5),
    benchmark_value DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_date ON market_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_opportunities_date ON opportunities(date);
CREATE INDEX IF NOT EXISTS idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_date ON portfolio_performance(date);

-- Enable Row Level Security (optional - customize based on your needs)
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_performance ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (allow all operations for authenticated users)
-- You can customize these policies based on your security requirements

CREATE POLICY "Enable all operations for authenticated users" ON market_data
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON opportunities
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON trades
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON positions
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON portfolio_performance
    FOR ALL USING (auth.role() = 'authenticated');

-- Insert sample data (optional)
-- Uncomment the following lines to add sample data for testing

/*
-- Sample market data
INSERT INTO market_data (symbol, date, open, high, low, close, volume) VALUES
('AAPL', '2024-01-01', 150.00, 155.00, 149.00, 153.50, 1000000),
('MSFT', '2024-01-01', 300.00, 305.00, 298.00, 302.75, 800000)
ON CONFLICT (symbol, date) DO NOTHING;

-- Sample opportunity
INSERT INTO opportunities (symbol, strategy, signal_strength, price, date, sector) VALUES
('AAPL', 'Technical', 0.75, 153.50, '2024-01-01', 'Technology')
ON CONFLICT DO NOTHING;
*/

-- Functions for data maintenance (optional)

-- Function to clean old market data (keep last 2 years)
CREATE OR REPLACE FUNCTION clean_old_market_data()
RETURNS void AS $$
BEGIN
    DELETE FROM market_data 
    WHERE date < CURRENT_DATE - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;

-- Function to update position PnL
CREATE OR REPLACE FUNCTION update_position_pnl(
    p_symbol VARCHAR(10),
    p_current_price DECIMAL(10,2)
)
RETURNS void AS $$
BEGIN
    UPDATE positions 
    SET pnl = (quantity * p_current_price) - (quantity * avg_cost),
        updated_at = NOW()
    WHERE symbol = p_symbol;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update positions table when trades are inserted
CREATE OR REPLACE FUNCTION update_position_on_trade()
RETURNS TRIGGER AS $$
DECLARE
    current_position RECORD;
    new_quantity INTEGER;
    new_avg_cost DECIMAL(10,2);
BEGIN
    -- Get current position
    SELECT * INTO current_position FROM positions WHERE symbol = NEW.symbol;
    
    IF current_position IS NULL THEN
        -- New position
        IF NEW.side = 'BUY' THEN
            INSERT INTO positions (symbol, quantity, avg_cost) 
            VALUES (NEW.symbol, NEW.quantity, NEW.price);
        ELSE
            INSERT INTO positions (symbol, quantity, avg_cost) 
            VALUES (NEW.symbol, -NEW.quantity, NEW.price);
        END IF;
    ELSE
        -- Update existing position
        IF NEW.side = 'BUY' THEN
            new_quantity := current_position.quantity + NEW.quantity;
            IF new_quantity != 0 THEN
                new_avg_cost := ((current_position.quantity * current_position.avg_cost) + (NEW.quantity * NEW.price)) / new_quantity;
            ELSE
                new_avg_cost := current_position.avg_cost;
            END IF;
        ELSE
            new_quantity := current_position.quantity - NEW.quantity;
            new_avg_cost := current_position.avg_cost; -- Keep same avg cost for sells
        END IF;
        
        UPDATE positions 
        SET quantity = new_quantity, 
            avg_cost = new_avg_cost,
            updated_at = NOW()
        WHERE symbol = NEW.symbol;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_position_on_trade ON trades;
CREATE TRIGGER trigger_update_position_on_trade
    AFTER INSERT ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_position_on_trade();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Success message
SELECT 'HedgeLab database schema created successfully!' AS message; 