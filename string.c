main(A) {
    B = A + test();
    printf(B);
    B = test() + 2;
    printf(B);
    return(0);
}

test() {
    B = 1;
    return(B);
}
