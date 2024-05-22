int s = 0;
int n = 1;
int ordA = 48;
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
int i = 1;
while(s/i){
    i = i*10;
}
i = i*10;
while(i-1){
    print(s/i+ordA);
    s = s%i;
    i = i/10;
}