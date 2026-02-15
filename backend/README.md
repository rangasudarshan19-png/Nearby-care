# Backend Setup Guide

## Quick Start

1. **Install Python Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup Environment Variables**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your configuration
```

3. **Run the Server**
```bash
python app.py
```

Server will be available at: `http://localhost:5000`

## API Configuration

### Using Free OpenStreetMap API (Default)
No configuration needed! Just run the server.

### Using Google Places API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Places API
   - Geocoding API
   - Maps JavaScript API
4. Create credentials (API Key)
5. Add to `.env`:
   ```
   GOOGLE_PLACES_API_KEY=your_api_key_here
   ```

## Database Options

### SQLite (Default - Development)
```env
DATABASE_URL=sqlite:///nearby_care.db
```

### PostgreSQL (Production)
```bash
# Install PostgreSQL
# Create database
createdb nearby_care

# Update .env
DATABASE_URL=postgresql://username:password@localhost:5432/nearby_care

# Install driver
pip install psycopg2-binary
```

### MySQL
```bash
# Install MySQL
# Create database
mysql -u root -p
CREATE DATABASE nearby_care;

# Update .env
DATABASE_URL=mysql://username:password@localhost:3306/nearby_care

# Install driver
pip install pymysql
```

## API Endpoints Testing

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Search hospitals
curl -X POST http://localhost:5000/api/search-hospitals-osm \
  -H "Content-Type: application/json" \
  -d '{"location":"New York","radius":5000}'

# Get favorites
curl http://localhost:5000/api/favorites?user_id=1
```

### Using Postman
Import the collection from `postman_collection.json`

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to 5001 or any available port
```

### CORS Issues
Make sure Flask-CORS is installed and configured in `app.py`

### Database Connection Errors
Check your DATABASE_URL in `.env` file
