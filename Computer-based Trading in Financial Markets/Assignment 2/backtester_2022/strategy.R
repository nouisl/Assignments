getOrders <- function(store, newRowList, currentPos, info, params) {
  ###########################################################################
  # You do not need to edit this next part of the code
  ###########################################################################
  allzero  <- rep(0,length(newRowList)) # used for initializing vectors
  pos <- allzero
  if (is.null(store)) 
    store <- initStore(newRowList)
  else
    store <- updateStore(store, newRowList)
  ###########################################################################
  ###########################################################################
  # This next code section is the only one you
  # need to edit for getOrders
  #
  # The if condition is already correct:
  # you should only start computing the moving 
  # averages when you have enough (close) prices 
  # for the long moving average 
  ###########################################################################
  if (store$iter > params$lookbacks$long) {
    # ENTER STRATEGY LOGIC HERE
    # remember to only consider the series in params$series
    # You will need to get the current_close
    # either from newRowList or from store$cl
    # You will also need to get prices 
    # from store$cl
    # With these you can use getTMA, getPosSignFromTMA
    # and getPosSize to assign positions to the vector pos
    
    lookbacks = params$lookbacks
    close_prices = store$cl
    current_close = list()
    
    for(i in 1:length(newRowList)){
      if (i %in% params$series){
        current_close[i] = newRowList[[i]]$Close
        pos_sign = getPosSignFromTMA(getTMA((close_prices[[i]]), lookbacks))
        pos[[i]] = getPosSize(current_close[[i]])*pos_sign
      }
    }
  }
  ###########################################################################
  ###########################################################################
  # You do not need to edit the rest of this function
  ###########################################################################
  marketOrders <- -currentPos + pos
  return(list(store=store,marketOrders=marketOrders,
              limitOrders1=allzero,limitPrices1=allzero,
              limitOrders2=allzero,limitPrices2=allzero))
}
###############################################################################
checkE01 <- function(prices, lookbacks) {
  # Return FALSE if lookbacks contains named elements short, medium, and long
  # otherwise return TRUE to indicate an error
  if ("short" %in% names(lookbacks) && "medium" %in% names(lookbacks) && "long" %in% names(lookbacks)){
    return(FALSE)
  }
  return(TRUE)
}
checkE02 <- function(prices, lookbacks) {
  # Return FALSE if all the elements of lookbacks are integers (as in the R
  # data type) otherwise return TRUE to indicate an error
  if (is.integer(lookbacks$short) && is.integer(lookbacks$medium) && is.integer(lookbacks$long)){
    return(FALSE)
  }
  return(TRUE)
}
checkE03 <- function(prices, lookbacks) {
  # Return FALSE if lookbacks$short < lookbacks$medium < lookbacks$long 
  # otherwise return TRUE to indicate an error
  if ((lookbacks$medium>lookbacks$short) && (lookbacks$long>lookbacks$medium)){
    return(FALSE)
  }
  return(TRUE)
}
checkE04 <- function(prices, lookbacks) {
  # Return FALSE if prices is an xts object, otherwise return TRUE to
  # indicate an error
  if (is.xts(prices)){
    return(FALSE)
  }
  return(TRUE)
}
checkE05 <- function(prices, lookbacks) {
  # Return FALSE if prices has enough rows to getTMA otherwise return TRUE
  # to indicate an error
  if (nrow(prices)>=lookbacks$long){
    return(FALSE)
  }
  return(TRUE)
}
checkE06 <- function(prices, lookbacks) {
  # Return FALSE if prices contains a column called "Close" otherwise return 
  # TRUE to indicate an error
  if ("Close" %in% names(prices)){
    return(FALSE)
  }
  return(TRUE)
}
###############################################################################
# You should not edit allChecks
atLeastOneError <- function(prices, lookbacks) {
  # return TRUE if any of the error checks return TRUE
  ret <- FALSE
  ret <- ret | checkE01(prices,lookbacks)
  ret <- ret | checkE02(prices,lookbacks)
  ret <- ret | checkE03(prices,lookbacks)
  ret <- ret | checkE04(prices,lookbacks)
  ret <- ret | checkE05(prices,lookbacks)
  ret <- ret | checkE06(prices,lookbacks)
  return(ret)
}
###############################################################################
getTMA <- function(prices, lookbacks, with_checks=FALSE) {
  # prices and lookbacks should pass (return FALSE) when used with
  # the 6 checks, as tested in the following call to allChecks that 
  # you should not edit
  if (with_checks){
    if (atLeastOneError(close_prices, lookbacks)){
      stop('At least one of the errors E01...E06 occured')
    }
  }
  ret <- 0
  # You need to replace the assignment to ret so that the returned object:
  #    - is a list 
  #    - has the right names (short, medium, long), and
  #    - contains numeric and not xts objects
  #    - and contains the correct moving average values, which should 
  #      have windows of the correct sizes that all end in the 
  #      same period, be the last row of prices
  long = SMA((prices$Close), n = lookbacks$long)
  medium = SMA((prices$Close), n = lookbacks$medium)
  short = SMA((prices$Close), n = lookbacks$short)
  
  ret = list(short = as.numeric(last(short)), medium = as.numeric(last(medium)), long = as.numeric(last(long)))
  
  return(ret)
}
getPosSignFromTMA <- function(tma_list) {
  # This function takes a list of numbers tma_list with three elements 
  # called short, medium, and long, which correspond to the SMA values for 
  # a short, medium and long lookback, respectively.
  # Note that if both this function and getTMA are correctly implemented 
  # then the following should work with correct input arguments:
  # getPositionFromTMA(getTMA(prices,lookbacks))
  # This function should return a single number that is:
  #       -1 if the short SMA < medium SMA < long SMA
  #        1 if the short SMA > medium SMA > long SMA
  #        0 otherwise
  
  short = tma_list$short
  medium = tma_list$medium
  long = tma_list$long
  
  pos = 0
  
  if(short < medium && medium < long){
    pos = -1
  } else if(short > medium && medium > long){
    pos = 1
  } else {
    pos = 0
  }
  
  return(pos)
}
getPosSize <- function(current_close,constant=5000) {
  # This function should return (constant divided by current_close) 
  # rounded down to the nearest integer
  pos_size = floor(constant/current_close)
  return(pos_size)
}
###############################################################################
# The functions below do NOT need to be edited
###############################################################################
initClStore  <- function(newRowList) {
  clStore <- lapply(newRowList, function(x) x$Close)
  return(clStore)
}
updateClStore <- function(clStore, newRowList) {
  clStore <- mapply(function(x,y) rbind(x,y$Close),clStore,newRowList,SIMPLIFY=FALSE)
  return(clStore)
}
initStore <- function(newRowList,series) {
  return(list(iter=1,cl=initClStore(newRowList)))
}
updateStore <- function(store, newRowList) {
  store$iter <- store$iter + 1
  store$cl <- updateClStore(store$cl,newRowList) 
  return(store)
}
