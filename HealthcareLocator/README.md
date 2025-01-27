# Nigerian Healthcare Facilities Explorer 🏥 🇳🇬

A comprehensive Streamlit-based geospatial web application for exploring and analyzing Nigerian healthcare facilities, offering advanced interactive mapping and user-centric healthcare management tools.

## Features

- Interactive geographical mapping with facility directions (driving, cycling, walking)
- Flexible authentication system with public and protected routes
- State and local government area (LGA) filtering system
- PostgreSQL database for secure data management
- Updated statistics showing Total Facilities across 36 States and LGA coverage
- Google Maps-style directions to healthcare facilities

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Streamlit account (for Streamlit Cloud deployment)

## Environment Variables

The following environment variables are required:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
PGUSER=your_db_user
PGPASSWORD=your_db_password
PGHOST=your_db_host
PGPORT=your_db_port
PGDATABASE=your_db_name
```

## Deployment Options

### 1. Streamlit Cloud (Recommended)

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from your forked repository
5. Set the required environment variables in the Streamlit Cloud dashboard
6. Deploy!

### 2. Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add a PostgreSQL database from Railway
4. Deploy the application
5. Railway will automatically set up the environment variables

### 3. Heroku

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login to Heroku:
   ```bash
   heroku login
   ```
3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
4. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
5. Deploy your application:
   ```bash
   git push heroku main
   ```

### 4. Local Deployment

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install streamlit folium sqlalchemy psycopg2-binary pandas numpy passlib python-jose python-multipart streamlit-folium
   ```
3. Set up your PostgreSQL database
4. Set the required environment variables
5. Run the application:
   ```bash
   streamlit run main.py --server.address=0.0.0.0 --server.port=5000 --server.headless=true
   ```

## Additional Configuration

- Ensure your PostgreSQL database is properly configured with SSL
- Configure your `.streamlit/config.toml` for custom theming and server settings
- Make sure your hosting provider supports WebSocket connections (required for Streamlit)

## Support

For technical support, please contact: admin@nhcservice.com

## License

This project is licensed under the MIT License - see the LICENSE file for details
