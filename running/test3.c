#include "../setlimits.c"
#include <stdio.h>

int main(int argc,char* argv[]){ setlimits(argc,argv);
    printf("Hello C World!!\n");
    return 0;
}    
