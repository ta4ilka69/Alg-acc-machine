char c = input();
int a = 5;
int b = a*5+6/2-3%2;
int ordA = 48;
while(c)
{
    print(c);
    c = input();
}
int i = 1;
while(b%i-b)
{
    i = i*10;
}
i = i/10;
while(i-1)
{
    print(b/i+ordA);
    b = b%i;
    i = i/10;
}
if(!b)
{
    print("bye!");
}
