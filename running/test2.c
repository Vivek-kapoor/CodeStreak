#include "../setlimits.c"
#include <stdio.h>

int main(int argc,char* argv[]){ setlimits(argc,argv);
    int n;
    scanf("%d",&n);
    int s=n*n;
    printf("%d",s);
    return 0;
}    
