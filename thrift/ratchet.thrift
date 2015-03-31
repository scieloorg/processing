exception ServerError {
    1: string message,
}

exception ValueError {
    1: string message,
}

service RatchetStats {
    string general(1:string code) throws (1:ValueError value_err, 2:ServerError server_err)
}