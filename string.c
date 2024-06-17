main(A) {
    B = test(A);
    A = A + B;
    printf(A);
    return(0);
}

test(X) {
    B = 1;
    X = X + B;
    return(X);
}
