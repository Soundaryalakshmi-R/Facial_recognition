const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const cors = require("cors");
const multer = require("multer");
const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();

// Initialize Express
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: { origin: process.env.FRONTEND_URL || "http://localhost:3000" },
});

// Middleware
app.use(cors());
app.use(express.json());
const upload = multer();

// Flask service URL
const FLASK_URL = process.env.FLASK_URL || "http://localhost:5000/api/face";
const RAG_URL = process.env.RAG_URL || "http://localhost:5001/api/chat";

// WebSocket for real-time face recognition
io.on("connection", (socket) => {
  console.log("Client connected");

  socket.on("recognize_face", async (imageData) => {
    try {
      // Send to Flask service
      const formData = new FormData();
      formData.append("image", imageData);

      const response = await axios.post(`${FLASK_URL}/recognize`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      socket.emit("recognition_result", response.data);
    } catch (error) {
      socket.emit("error", { message: "Recognition failed" });
    }
  });

  socket.on("disconnect", () => {
    console.log("Client disconnected");
  });
});

// API Routes
app.post("/api/users", async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_URL}/users`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ success: false, message: "User creation failed" });
  }
});

app.post("/api/register-face", upload.single("image"), async (req, res) => {
  try {
    const formData = new FormData();
    formData.append("user_id", req.body.user_id);
    formData.append("image", req.file.buffer, { filename: "face.jpg" });

    const response = await axios.post(`${FLASK_URL}/register`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    res.json(response.data);
  } catch (error) {
    res
      .status(500)
      .json({ success: false, message: "Face registration failed" });
  }
});

// Chat with RAG
app.post("/api/chat", async (req, res) => {
  try {
    const response = await axios.post(RAG_URL, { message: req.body.message });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ success: false, message: "Chat processing failed" });
  }
});

// Start server
const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
