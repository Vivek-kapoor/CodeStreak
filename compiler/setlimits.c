#include <sys/resource.h> 
#include <sys/time.h> 
#include <stdlib.h>
#include <unistd.h> 
#include<signal.h>
#include<stdio.h> 
#include<stdbool.h>

 // Define the function to be called when ctrl-c (SIGINT) signal is sent to process
void
signal_callback_handler(int signum)
{
   printf("TLE: TIME LIMIT EXCEEDED \n");
   exit(signum);
}


 int setlimits(int argc, char* argv[]) 
 { 
   struct rlimit rl; 
   bool defaultv = false;
   if(argc<2){
      defaultv = true;
   }
   //default time out
   int time_to_set = 5;
   if(!defaultv){
      time_to_set = atoi(argv[1]);
   }
   signal(SIGXCPU, signal_callback_handler);
   // First get the time limit on CPU 
   getrlimit (RLIMIT_CPU, &rl); 
   // Change the time limit 
   rl.rlim_cur = time_to_set; 
   // Now call setrlimit() to set the  
   // changed value. 
   setrlimit (RLIMIT_CPU, &rl); 

   // Change the limit 
   rl.rlim_cur = 3; // 3 are for stdin, stdout, stderr and one extra 
  
   // Now call setrlimit() to set the  
   // changed value. 
   setrlimit (RLIMIT_NOFILE, &rl);   
  // First get the limit on number of child processes
  getrlimit (RLIMIT_NPROC, &rl);

  // Change the limit
  rl.rlim_cur = 0; // Now we do not want this process to have any child process

  // Now call setrlimit() to set the 
  // changed value.
  setrlimit (RLIMIT_NPROC, &rl);

   return 0; 
 }