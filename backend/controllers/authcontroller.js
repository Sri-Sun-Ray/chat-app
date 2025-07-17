const User=require('../models/User');
const bcrypt=require('bcryptjs');
const jwt=require('jsonwebtoken');

// Registration

exports.register= async(req,res)=>{
    try{
        const {username,email,password}=req.body;
        
        // checking if username or email already exists.
        const existingUser=await User.findOne({$or: [{username},{email}]});

        if(existingUser){
            return res.status(400).json({message: 'User already exists'});
        }

        // Hash password

        const salt=await bcrypt.genSalt(9); // Salt is string which is unique for each user
        const hashedpassword= await bcrypt.hash(password,salt);

        // Creating User

        const newUser= new User({
            username, email, 
            password: hashedpassword
        });

        // save the user to the database

        await newUser.save();
        res.status(201).json({message: 'User registered succesfully'});


    }
    catch(err){
        console.error(err);
        res.status(500).json({message: 'Server error during registration'});
    }
};   

// Login Code

exports.login= async(req,res)=>{
    try{
        const {email,password}=req.body;

        // find if user there

        const user=await User.findOne({email});
        if(!user) return res.status(400).json({message: 'Invalid credentials'});

        //Password Comparision

        const isMatch=await bcrypt.compare(password,user.password);
        if(!isMatch) return res.status(400).json({message: 'Password doesn\'t match'});

        // Generating JavaWebToken

        const token=jwt.sign({id: user._id,username: user.username},process.env.JWT_SECRET,{expiresIn:'7d'});

        // sending response

        res.status(200).json({
            token,
            user:{
                id: user._id,
                username: user.username,
                avatar: user.avatar,
                email: user.email,
            }
        });
    
    }
    catch(err){
        console.error(err);
        res.status(500).json({message: 'Server Error during login'});
    }
};

/* eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4Nzc5MWE3ODI1MGQ4ODkxZTU0YzdmOCIsInVzZXJuYW1lIjoic3VyeWEiLCJpYXQiOjE3NTI2NjY3MDgsImV4cCI6MTc1MzI3MTUwOH0.l1xuJszW2ahpN2h21frhkbU6bRFf1WcB3N1kg1wsqMw*/