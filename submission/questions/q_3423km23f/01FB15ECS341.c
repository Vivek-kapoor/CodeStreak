#include "../setlimits.c"
#include <stdio.h>

int main(int argc,char* argv[]){ setlimits(argc,argv);
    int a;
    scanf("%d",&a);
    int s=a*a;
    printf("%d",s);
    
    return 0;
}    
