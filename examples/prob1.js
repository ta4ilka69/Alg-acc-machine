int s = 0;
int n = 1;
while(1000-n){
    if(!n%5){
        s = s + n;
    }
    if(n%5){
        if(!n%3){
            s = s + n;
        }
    }
    n = n + 1;
}