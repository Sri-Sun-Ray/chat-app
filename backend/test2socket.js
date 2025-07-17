const {io}=require("socket.io-client");

// sender niharika
const socket=io("http://localhost:5000",{
    auth: {
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4Nzg3ZTE5ODQ1NzFjNWIxZTAzMTJiNCIsInVzZXJuYW1lIjoiTmloYXJpa2EiLCJpYXQiOjE3NTI3MzU3MDMsImV4cCI6MTc1MzM0MDUwM30.P6L8OUZrDfSfhJlx43UUyj1JW519Tv1gvwGY_iGF4ow"
    }
});

socket.on("connect",()=>{
    console.log("Connected as:",socket.id);

    socket.emit("send_message",{
        to: "687891f7dd365e7b66c1e987",
        content: "I am Good"
    });

});

socket.on("receive_message",(data)=>{
    console.log("New message received:",data);
});

socket.on("disconnect",()=>
{
    console.log("Disconnected");
});