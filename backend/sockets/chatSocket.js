const jwt = require('jsonwebtoken');
const Message = require('../models/Message');
const User = require('../models/User');

const connectedUsers = new Map(); // key: userId, value: socket.id

module.exports = (io) => {
    // Middleware for token auth
    io.use((socket, next) => {
        const token = socket.handshake.auth.token;
        if (!token) return next(new Error("Authentication Error: Token missing"));

        try {
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            socket.user = decoded;
            next();
        } catch (err) {
            next(new Error("Authentication Error: Invalid Token"));
        }
    });

    io.on('connection', async (socket) => {
        const userId = socket.user.id;
        console.log(`User connected: ${userId}`);
        connectedUsers.set(userId, socket.id);

        // Set user online
        await User.findByIdAndUpdate(userId, {
            isOnline: true,
            lastSeen: new Date(),
        });

        // Send Message
        socket.on('send_message', async ({ to, content }) => {
            console.log('Received message', { from: userId, to, content });
            try {
                const message = new Message({
                    sender: userId,
                    receiver: to,
                    content,
                });

                await message.save();
                console.log("Message saved to DB:", message);

                // Emit to receiver if online
                const receiverSocket = connectedUsers.get(to);
                if (receiverSocket) {
                    io.to(receiverSocket).emit('receive_message', {
                        from: userId,
                        content,
                        createdAt: message.createdAt,
                    });
                }
            } catch (err) {
                console.log("Send message error: ", err);
            }
        });

        // Read receipt
        socket.on('message_read', async ({ messageId }) => {
            await Message.findByIdAndUpdate(messageId, { isRead: true });
        });

        // Disconnect
        socket.on('disconnect', async () => {
            console.log(`User Disconnected: ${userId}`);
            connectedUsers.delete(userId);
            await User.findByIdAndUpdate(userId, {
                isOnline: false,
                lastSeen: new Date(),
            });
        });
    });
};
