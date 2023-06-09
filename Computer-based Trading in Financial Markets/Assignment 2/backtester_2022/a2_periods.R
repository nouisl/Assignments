charToDigit <- function(string,i,const)
    (i+const)*strtoi(substr(string,start=i,stop=i),36L)

getDigits <- function(string,const) 
    sapply(1:nchar(string),function(x) charToDigit(string,x,const))

library(digest)
getPeriods <- function(user) {
    CONSTANT <- 600 
    dig <- digest(user,'crc32')
    startIn <- 1
    endIn <- round(sum(getDigits(dig,0))) + CONSTANT
    startOut <- endIn + 1
    endOut <- 2000
    periods = list(startIn=startIn,
                   endIn=endIn,
                   startOut=startOut,
                   endOut=endOut)
    return(periods)
}
  
paramssss <- function(params)
  return(params$series)

getIns <- function(user) {
  
}

getOut <- function(user) {
  
  
}

