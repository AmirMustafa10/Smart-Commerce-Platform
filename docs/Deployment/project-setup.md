# Project Setup

## Core Application

The project includes a dedicated `core` application for shared pages, common templates, and project-wide functionality.

## Authentication Configuration

Authentication redirects are centralized using Django settings.

- `LOGIN_REDIRECT_URL`
- `LOGOUT_REDIRECT_URL`

## Database Configuration

The project uses `dj-database-url` to support environment-based database configuration.

This allows seamless switching between SQLite for local development and PostgreSQL in production without changing application code.

## Static & Media

Static and media files are configured from the beginning to support future assets such as product images and store logos.

## Templates

A global templates directory is configured to host shared templates across applications.

## Crispy Forms

The project uses Crispy Forms with the Bootstrap 5 template pack to provide consistent form rendering and reduce repetitive HTML.
Crispy Forms is used throughout the authentication pages to ensure consistent styling and reduce repetitive template code.