const {io}=require("socket.io-client");

const socket=io("http://localhost:5000",{
    auth: {
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4Nzg3ZTE5ODQ1NzFjNWIxZTAzMTJiNCIsInVzZXJuYW1lIjoiTmloYXJpa2EiLCJpYXQiOjE3NTI3MzU3MDMsImV4cCI6MTc1MzM0MDUwM30.P6L8OUZrDfSfhJlx43UUyj1JW519Tv1gvwGY_iGF4ow"
    }
});

socket.on("connect",()=>
{
    console.log("Receiver Connected:",socket.id);
});

socket.on("receive_message",(data)=>{
    console.log("New Message Received:",data);
});

socket.on("disconnect",()=>{
    console.log("Receiver disconnected");
});
