#include "../setlimits.c"
#include <stdio.h>

int main(int argc,char* argv[]){ setlimits(argc,argv);
    printf("Hello C World!!\n");
    int * ar;
    ar = (int *) malloc(sizeof(int) * 1000000000);
    while(1)
    {
        continue;
    }
    ar[0]=1;
    return 0;
}    
