# Overview

NaijaPay is a digital wallet application built specifically for Nigeria, enabling users to send and receive money securely through a web-based platform. The application provides core features like user registration, wallet management, money transfers, and transaction history tracking. It's designed as a Flask-based web application with a focus on Nigerian users, including support for Nigerian phone number validation and Naira currency formatting.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with PostgreSQL support via environment variables
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Form Handling**: WTForms with Flask-WTF for CSRF protection
- **Session Management**: Flask sessions with configurable secret keys

## Data Model Design
- **User Model**: Stores user credentials, personal information, and account metadata
- **Wallet Model**: One-to-one relationship with users, manages balance and unique wallet numbers
- **Transaction Model**: Tracks money transfers between users with references and status tracking
- **Relationships**: Foreign key relationships between users, wallets, and transactions

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **Styling**: Custom CSS with Nigerian-themed colors (green/white)
- **JavaScript**: Vanilla JS for form validation, currency formatting, and UI enhancements
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

## Security Implementation
- **Password Security**: Werkzeug password hashing with salted hashes
- **CSRF Protection**: Flask-WTF tokens on all forms
- **Input Validation**: Server-side validation with WTForms validators
- **Session Security**: Configurable session secrets and secure cookie handling

## Business Logic
- **Wallet System**: Automatic wallet creation with unique 10-digit numbers
- **Transaction Processing**: Atomic operations for money transfers with reference generation
- **Nigerian Focus**: Phone number validation for Nigerian formats, Naira currency display
- **User Experience**: Dashboard-centric design with quick actions and transaction history

## Database Schema
- **Users Table**: Authentication and profile data with timestamps
- **Wallets Table**: Balance management with unique identifiers
- **Transactions Table**: Transfer records with sender/receiver relationships
- **Indexing**: Primary keys and unique constraints on critical fields

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and query builder
- **Flask-Login**: User session management
- **WTForms**: Form validation and rendering
- **Werkzeug**: Password hashing and security utilities

## Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme variant
- **Font Awesome**: Icon library for user interface
- **Custom CSS**: Nigerian-themed styling and responsive design

## Development Tools
- **Logging**: Python logging for debugging and monitoring
- **ProxyFix**: Werkzeug middleware for deployment behind proxies
- **Environment Variables**: Configuration management for database URLs and secrets

## Database Configuration
- **SQLite**: Default development database
- **PostgreSQL**: Production database support via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability