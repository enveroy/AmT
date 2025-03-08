# Laboratory Chemical Management System

A web-based application for tracking chemical borrowing, indent management, and inventory control in laboratory environments.

## Overview

This system provides a comprehensive solution for laboratories to:
- Track chemicals borrowed from the lab inventory with detailed borrower information
- Manage and validate indent requests from lab members
- Process chemical returns and reconcile inventory
- Export approved indents as CSV files for record-keeping and analysis

## Architecture

### Frontend
- Hosted on [Render](https://render.com/)
- Responsive interface for desktop and mobile access
- Intuitive dashboard for quick monitoring of current borrowings and pending indents

### Backend
- PostgreSQL database hosted on [Neon](https://neon.tech/)
- Two primary tables: 
  - `borrowed_chemicals`: Tracks borrowed chemicals and borrower details
  - `indent`: Manages indent requests and approval status

## Features

- **Chemical Borrowing Management**
  - Record borrower details and borrowed chemicals
  - Set expected return dates
  - Mark chemicals as returned
  - Track borrowing history

- **Indent Processing**
  - Submit new indent requests
  - Review and validate indent requests
  - Export approved indents as CSV files
  - Maintain audit trail of all indent activities

- **Automated Maintenance**
  - Scheduled background thread runs every 2 months
  - Automatically purges database entries older than 6 months
  - Ensures compliance with data retention policies
  - Maintains optimal database performance with VACUUM ANALYZE

## Technologies Used

### Backend
- **Flask**: Web framework for building the application
- **PostgreSQL**: Database system (hosted on Neon)
- **psycopg2**: PostgreSQL adapter for Python
- **Gunicorn**: WSGI HTTP server for production deployment

### Features & Implementation
- **Connection Pooling**: Efficient database connection management
- **Pagination**: Implemented for listing borrowed chemicals and indents
- **CSV Export**: Functionality to export approved indents
- **Background Processing**: Threading for scheduled maintenance tasks
- **Environment Variables**: Secure configuration management

### Security & Best Practices
- **Parameterized Queries**: Prevention of SQL injection attacks
- **Error Handling**: Graceful error management
- **SSL Mode**: Secure database connections
- **Production/Development Configurations**: Separate configs for different environments

## Deployment

The application uses a modern cloud-native architecture:
- Frontend deployed on Render for reliable hosting and automatic scaling
- Backend database hosted on Neon for serverless PostgreSQL capabilities
- Scheduled maintenance tasks for database optimization

## Getting Started

1. Clone the repository
2. Set up environment variables:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `SECRET_KEY`: A secure secret key for Flask
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `gunicorn app:app`

## Contributing

This project was developed by Alan.

If you're interested in contributing to this project:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
