#include "../setlimits.c"
#include <stdio.h>

int main(int argc,char* argv[]){ setlimits(argc,argv);
    int n;
    scanf("%d",&n);
    printf("%d",n);
    return 0;
}    
