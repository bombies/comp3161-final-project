# COMP3161 Final Project

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.6 or higher
- pip (Python package installer)

## Setup

Follow these steps to get your development environment set up:

### 1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/bombies/comp3161-final-project.git
cd comp3161-final-project
```

### 2. Create a Virtual Environment

It's recommended to create a virtual environment to manage dependencies separately from other Python projects.

```bash
python -m venv venv
```

You then need to activate the virtual environment:

- On Windows:
```bash
venv\Scripts\activate
```

- On MacOS and Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

This project uses MariaDB/MySQL as it's database provider, so you will need your own database credentials to ensure the app works properly.

Take a look at the `.env.example` file and copy and paste the keys into a new `.env` file. From there, you can fill in the values accordingly.

```env
# comp3161-final-project/.env

DATABASE_HOST=localhost
DATABASE_USER=mysql
DATABASE_PASSWORD=password
DATABASE=University
DATABASE_PORT=3306

MASTER_PASSWORD=password
JWT_SECRET=secret

DEBUG=False
```

> [!IMPORTANT]
> The `MASTER_PASSWORD` field is used to set the password for the root user on initial creation. The email for the root user will always be `root`. You can use that account when you need Admin privileges on the API.

> [!NOTE]
> The `JWT_SECRET` field it just a string that will be used to sign the JWT tokens generated to ensure message integrity for authorization purposes.

> [!NOTE]
> The `DEBUG` field is mainly for enabling hot-reloads during active development. The field itself can effectively be omitted.

### 5. Initialize Database

Ensure you run the `init.sql` file in the `scripts` directory before serving the application. If this is not done an error will be thrown.

### 6. Serve the Application

Start the flask application with:

```bash
python run.py
```

## Extras

- When accessing endpoints that require authorization, ensure you have received a JWT token by logging in through the `POST /auth/login` endpoint. Copy the token and send a request to the protected route with the following header: `Authorization: <your_token_here>`