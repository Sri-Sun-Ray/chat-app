const { io } = require("socket.io-client");

// Sender Token: SURYA
const socket = io("http://localhost:5000", {
    auth: {
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4Nzg5MWY3ZGQzNjVlN2I2NmMxZTk4NyIsInVzZXJuYW1lIjoiU3VyeWEgS2lyYW4iLCJpYXQiOjE3NTI3MzIxNjUsImV4cCI6MTc1MzMzNjk2NX0.Jfag1DnXura3VVgBVZKX8H6S1iFB4N10nDtEqrvyDYk"
    }
});

socket.on("connect", () => {
    console.log("Connected as:", socket.id);

    socket.emit("send_message", {
        to: "68787e1984571c5b1e0312b4", // Receiver: Niharika
        content: "How are you",
    });
});

socket.on("receive_message", (data) => {
    console.log("New message received:", data);
});

socket.on("disconnect", () => {
    console.log("Disconnected");
});
