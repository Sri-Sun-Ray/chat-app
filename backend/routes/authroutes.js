const express=require('express');
const router=express.Router();

//Import register and login from auth controllers

const {register, login}=require('../controllers/authcontroller');

//@ route POST/api/auth/register
router.post('/register',register);

// @ route POST/api/auth/login

router.post('/login',login);

module.exports=router;
