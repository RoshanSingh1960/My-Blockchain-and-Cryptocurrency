pragma solidity ^0.8.7;

contract mycrypto_ico{

 //introducing the maximum number of mycrypto avilable for sale 
   uint public max_mycrypto = 1000000;

 
 //introducing usd to mycrypto conversion rate
   uint public usd_to_mycrypto = 1000;

//introducing total number of mycrypto  that haveen brought by the investors
   uint public total_mycrypto_bought = 0;

//mapping from the investor address to its equity in mycrypto and USD
mapping(address => uint) equity_mycrypto;
mapping(address => uint) equity_usd;


}