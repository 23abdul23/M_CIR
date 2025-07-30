# Warrior Support System

## Overview
The Warrior Support System is a comprehensive platform designed to manage personnel, battalions, and examinations for military operations. It provides a Commanding Officer (CO) dashboard for managing approvals, viewing statistics, and handling personnel data efficiently.

## Features
- **Personnel Management**: Add, update, and delete personnel records.
- **Battalion Management**: Approve or reject battalion requests.
- **Examination Management**: Add and manage examination questions.
- **Role-Based Access Control**: Different roles (CO, JSO, USER) with specific permissions.
- **Dashboard Statistics**: View statistics for battalions, pending approvals, and examination questions.

## Project Structure
```
warrior-support-system/
├── backend/
│   ├── routes/          # API routes for personnel, battalions, etc.
│   ├── models/          # Mongoose models for database schema
│   ├── middleware/      # Authentication and authorization middleware
│   └── server.js        # Entry point for the backend server
├── src/
│   ├── components/      # React components for the frontend
│   ├── styles/          # CSS styles for the application
│   └── App.jsx          # Main React application file
├── public/              # Static assets
├── README.md            # Project documentation
└── package.json         # Project dependencies and scripts
```

## Installation

### Prerequisites
- Node.js (v14 or later)
- MongoDB

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/23abdul23/M_CIR.git
   cd M_CIR
   ```
2. Install dependencies for both backend and frontend:
   ```bash
   cd warrior-support-system/backend
   npm install
   cd ../src
   npm install
   ```
3. Set up environment variables:
   - Create a `.env` file in the `backend` folder with the following:
     ```env
     MONGO_URI=<your-mongodb-connection-string>
     JWT_SECRET=<your-jwt-secret>
     ```
4. Start the backend server:
   ```bash
   cd warrior-support-system/backend
   npm start
   ```
5. Start the python backend:
   ```bash
   cd warrior-support-system/python-backend
   uvicorn app:app --reload
   ```
6. Start the frontend:
   ```bash
   cd warrior-support-system
   npm start
   ```

## Usage
1. Access the application at `http://localhost:3000`.
2. Log in as a Commanding Officer to manage personnel and battalions.
3. Use the dashboard to view statistics and perform quick actions.

## API Endpoints
### Personnel
- `GET /api/personnel/pending`: Fetch pending personnel approvals.
- `PUT /api/personnel/approve-user/:id`: Approve or reject a user.

### Battalions
- `GET /api/battalion`: Fetch all battalions.
- `PATCH /api/battalion/:id/status`: Update battalion status.

### Questions
- `GET /api/questions`: Fetch all examination questions.
- `POST /api/questions`: Add a new question.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- Special thanks to the contributors and the open-source community for their support.