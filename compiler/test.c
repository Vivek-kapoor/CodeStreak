#include<stdio.h>
#include<stdlib.h>
int main(int argc, char* argv[]){
	setlimits(argc,argv);
  // to test memory -  defult limit is 5024 bytes
	int* arr = malloc(sizeof(int)*1000000);
  //timeouot limit - 5 seconds
	for(int i=0;i<1000000;i++){
		for(int j=0;j<100000;j++){
			;
		}
	}
	//Try opening more than one file 
  
   FILE *fp = NULL; 
  
   int i=0; 
  
   for (i=0; i<2; i++) 
   { 
       fp = NULL; 
       fp = fopen("test.txt","r"); 
       if(NULL == fp) 
       { 
           printf("\n fopen failed [%d]\n", i); 
           
       } 
   } 
    // Try creating a process

  if( -1 == fork())
  {
      printf("\n Creating a child process failed\n");
  }

	return 0;
}