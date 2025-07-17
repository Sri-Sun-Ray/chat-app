//backend code
const express=require('express');
const http=require('http');
const cors=require('cors');
const mongoose=require('mongoose');
const dotenv=require('dotenv'); 
const { Server }=require('socket.io');

// dotenv addition
dotenv.config();

// creating the instances
const app=express();
const server=http.createServer(app);
const io=new Server(server,{cors:{origin:'*'}});

app.use(express.json());

const authRoutes=require('./routes/authroutes.js');
app.use('/api/auth',authRoutes);





//enabling cors and express.json to the app created using express backend
app.use(cors());


// MongoDB connection enabling to the server.js using mongoose
/*mongoose.connect(process.env.MONGO_URI,{
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(()=> console.log('MongoDB Connected')).catch(err=> console.log(err));*/

mongoose.connect(process.env.MONGO_URI).then(()=>{
    console.log("MongoDB connected")}).catch(err=>{console.log(err)})


// Basic Route

app.get('/',(req,res)=>{
    res.send('Chat App Backend Running');
});

// Routes


// Socket ID setup

/*io.on('connection',(socket)=>{
    console.log('new cient connected:',socket.id);

    socket.on('message',(data)=>{
        console.log('message recieved: ',data);
        io.emit('message',data);
    });
    socket.on('disconnect',()=>{
        console.log('client disconnected:',socket.id);
    });
});*/

const chatSocket=require('./sockets/chatSocket.js');
chatSocket(io);


const PORT=process.env.PORT || 5000;
server.listen(PORT,()=>console.log(`Server running on port ${PORT}`));

