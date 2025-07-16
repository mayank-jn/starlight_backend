-- Supabase Schema for Starlight Astrology API
-- User Profile Management Tables

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
    longitude DECIMAL(11, 8) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    created_at TIMESTAMP(3) WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP(3) WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for user_profiles
-- Users can only see/modify their own profiles
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own profile" ON user_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;

-- Create function to get user profile by user_id
CREATE OR REPLACE FUNCTION get_user_profile(user_uuid UUID)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    name VARCHAR(255),
    birth_date DATE,
    birth_time TIME,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    timezone VARCHAR(50),
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.user_id,
        p.name,
        p.birth_date,
        p.birth_time,
        p.latitude,
        p.longitude,
        p.timezone,
        p.city,
        p.state,
        p.country,
        p.created_at,
        p.updated_at
    FROM user_profiles p
    WHERE p.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if profile exists
CREATE OR REPLACE FUNCTION profile_exists(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS(SELECT 1 FROM user_profiles WHERE user_id = user_uuid);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Example data (optional - remove in production)
-- INSERT INTO user_profiles (user_id, name, birth_date, birth_time, latitude, longitude, timezone, city, state, country)
-- VALUES (
--     'your-user-id-here',
--     'John Doe',
--     '1990-01-15',
--     '14:30:00',
--     40.7128,
--     -74.0060,
--     'America/New_York',
--     'New York',
--     'NY',
--     'USA'
-- );

-- Comments for documentation
COMMENT ON TABLE user_profiles IS 'User profile information including birth details for astrological calculations';
COMMENT ON COLUMN user_profiles.user_id IS 'Foreign key to auth.users.id';
COMMENT ON COLUMN user_profiles.birth_date IS 'Date of birth in YYYY-MM-DD format';
COMMENT ON COLUMN user_profiles.birth_time IS 'Time of birth in HH:MM format';
COMMENT ON COLUMN user_profiles.latitude IS 'Birth location latitude (-90 to 90)';
COMMENT ON COLUMN user_profiles.longitude IS 'Birth location longitude (-180 to 180)';

-- Create birth_chart_details table
CREATE TABLE IF NOT EXISTS birth_chart_details (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    planet_positions JSONB NOT NULL,
    chart_image BYTEA NOT NULL,
    created_at TIMESTAMP(3) WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP(3) WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_birth_chart_details_user_id ON birth_chart_details(user_id);

-- Create updated_at trigger for birth_chart_details
CREATE TRIGGER update_birth_chart_details_updated_at
    BEFORE UPDATE ON birth_chart_details
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE birth_chart_details ENABLE ROW LEVEL SECURITY;

-- Create policies for birth_chart_details
CREATE POLICY "Users can view their own chart details" ON birth_chart_details
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chart details" ON birth_chart_details
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own chart details" ON birth_chart_details
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chart details" ON birth_chart_details
    FOR DELETE USING (auth.uid() = user_id);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON birth_chart_details TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE birth_chart_details IS 'Stores user birth chart details including planet positions and chart image';
COMMENT ON COLUMN birth_chart_details.planet_positions IS 'JSON array of planet positions with signs and degrees';
COMMENT ON COLUMN birth_chart_details.chart_image IS 'Binary data of the birth chart image';