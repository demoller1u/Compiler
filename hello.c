main(X, Y) {
    A = 0;
    while(X){
        X = X-1;
        Y = Y+1;
    }
    printf(Y);
    X = test(Y,20);
    printf(Y);
    return(Y);
}
test(X,Y) {
    D = X + Y;
    X = X + 1;
    X = X + D;
    return(X);
}
