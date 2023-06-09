book.total_volumes <- function(book) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #
  # Returns:
  #   The total volume in the book.
  
  total_volumes <- list ("ask" = sum(book[[1]] [,3]), "bid" = sum(book[[2]] [,3]))
  return (total_volumes)
}
book.best_prices <- function(book) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #
  # Returns:
  #   A list with "ask" and "bid", the values of which are the best prices in
  #       the book.
  
  best_prices <- list ("ask" = min(book[[1]] [,2]), "bid" = max(book[[2]] [,2]))
  return (best_prices)
}
book.midprice <- function(book) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #
  # Returns:
  #   The midprice of the book.
  
  midprice <- ((min(book[[1]] [,2])) + (max(book[[2]] [,2])))/2
  return(midprice)
}
book.spread <- function(book) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #
  # Returns:
  #   The spread of the book.
  
  spread <- (min(book[[1]] [,2])) - (max(book[[2]] [,2]))
  return(spread)
}
book.add <- function(book, message) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #   message - A list containing "oid", "side", "price" and "size" entries.
  #
  # Returns:
  #   The updated book.
  
  a <- nrow(book[[2]])
  b <- 0
  c <- nrow(book[[1]])
  d <- 0
  book = book.sort(book)
  if (message[[2]] == "S") {
    if (message$price > max(book[[2]] [,2])){
      book[[1]] <- data.frame(oid = c(book[[1]][,1], message$oid), 
                              price = c(book[[1]][,2], message$price), 
                              size = c(book[[1]][,3], message$size))
    } else {
      for (j in 1:nrow(book[[2]])){
        if (book[[2]][j,2] < message$price & message$size > 0) {
          book[[1]] <- data.frame(oid = c(book[[1]][,1], message$oid), 
                                  price = c(book[[1]][,2], message$price), 
                                  size = c(book[[1]][,3], message$size))
          message$size <- 0
          break 
        } else if (book[[2]][j,3] - message$size == 0){
          book[[2]] <- book[[2]][-j, ]
          message$size <- 0
          break
        } else if (book[[2]][j,3] - message$size > 0){
          book[[2]][j,3] <- book[[2]][j,3] - message$size
          message$size <- 0
          break
        } else if (book[[2]][j,3] - message$size < 0){
          message$size <- message$size - book[[2]][j,3]
          b <- b + 1
        } 
      }
      if (b > 0) {
        book[[2]] <- book[[2]][-(1:b), ]
      }
      a <- nrow(book[[2]])
      if (a == 0 & message$size > 0) {
        book[[1]] <- data.frame(oid = c(book[[1]][,1], message$oid), 
                                price = c(book[[1]][,2], message$price), 
                                size = c(book[[1]][,3], message$size))
        message$size <- 0
      }
    }
  } else if (message[[2]] == "B") {
    if (message$price < min(book[[1]] [,2])){
      book[[2]] <- data.frame(oid = c(book[[2]][,1], message$oid), 
                              price = c(book[[2]][,2], message$price), 
                              size = c(book[[2]][,3], message$size))
    } else {
      for (j in 1:nrow(book[[1]])){
        if (book[[1]][j,2] > message$price & message$size > 0) {
          book[[2]] <- data.frame(oid = c(book[[2]][,1], message$oid), 
                                  price = c(book[[2]][,2], message$price), 
                                  size = c(book[[2]][,3], message$size))
          message$size <- 0
          break 
        } else if (book[[1]][j,3] - message$size == 0){
          book[[1]] <- book[[1]][-j, ]
          message$size <- 0
          break
        } else if (book[[1]][j,3] - message$size > 0){
          book[[1]][j,3] <- book[[1]][j,3] - message$size
          message$size <- 0
          break
        } else if (book[[1]][j,3] - message$size < 0){
          message$size <- message$size - book[[1]][j,3]
          d <- d + 1
        }
      }
      if (d > 0) {
        book[[1]] <- book[[1]][-(1:d), ]
      }
      c <- nrow(book[[1]])
      if (c == 0 & message$size > 0) {
        book[[2]] <- data.frame(oid = c(book[[2]][,1], message$oid), 
                                price = c(book[[2]][,2], message$price), 
                                size = c(book[[2]][,3], message$size))
        message$size <- 0
      }
    }
  }
  return(book)
}
book.reduce <- function(book, message) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #   message - A list containing "oid" and "amount".
  #
  # Returns:
  #   The updated book.
  
  for (i in 1:length(book)){
    for (j in 1:nrow(book[[i]])){
      if (book[[i]][j,1] == message[[1]]){
        book[[i]][j,3] <- book[[i]][j,3] - message[[2]]
        if (book[[i]][j,3] <= 0) {
          book[[i]] <- book[[i]][-j, ]
        }
        break
      } 
    }
  }
  return(book)
}
###############################################################################
###############################################################################
# The following functions are the "extra" functions; marks for these functions
# are only available if you have fully correct implementations for the 6
# functions above

book.extra1 <- function(book, size) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #   size - An integer between 1 and M, where M is the total volume of the ask
  #       book.
  #
  # Returns:
  #   The updated midprice.
  
  book = book.sort(book)
  prices <- list()
  m <- 0
  for (i in 1:nrow(book[[1]])){
    m <- m + book[[1]][i,3] 
  }
  if (m == size) {
    midprice = NA
  } else {
    for (i in 1:nrow(book[[1]])){
      prices <- append(prices, book[[1]][i,2])
    }
    price <- sample(prices,1)
    price <- as.numeric(unlist(price))
    message <- list("x1", "B", price ,size)
    names(message) <- c("oid", "side", "price", "size")
    book <- book.add(book, message)
    midprice <- book.midprice(book)
  }
  return (midprice)
}
book.extra2 <- function(book, size) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #   size - An integer between 1 and M, where M is the total volume of the ask
  #       book.
  #
  # Returns:
  #   The updated midprice.
  
  book = book.sort(book)
  prices <- list()
  m <- 0
  for (i in 1:nrow(book[[1]])){
    m <- m + book[[1]][i,3] 
  }
  if (m == size) {
    midprice = NA
  } else {
    for (i in min(book[[1]][,2]):max(book[[1]][,2])){
      prices <- append(prices, i)
    }
    price <- sample(prices,1)
    price <- as.numeric(unlist(price))
    message <- list("x2", "B", price ,size)
    names(message) <- c("oid", "side", "price", "size")
    book <- book.add(book, message)
    midprice <- book.midprice(book)
  }
  return (midprice)
}
book.extra3 <- function(book) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #
  # Returns:
  #   The updated midprice.
  
  book = book.sort(book)
  prices <- list()
  sizes <- list ()
  m <- 0
  for (i in 1:nrow(book[[1]])){
    m <- m + book[[1]][i,3] 
  }
  for (j in 1:m-1){
    sizes <- append(sizes, j)
  }
  size <- sample(sizes, 1)
  size <- as.numeric(unlist(size))
  for (i in min(book[[1]][,2]):max(book[[1]][,2])){
    prices <- append(prices, i)
  }
  price <- sample(prices,1)
  price <- as.numeric(unlist(price))
  message <- list("x3", "B", price ,size)
  names(message) <- c("oid", "side", "price", "size")
  book <- book.add(book, message)
  midprice <- book.midprice(book)
  
  return (midprice)
}
book.extra4 <- function(book, k) {
  # Arguments:
  #   book - A list containing "ask" and "bid", each of which are dataframes
  #       containing the collection of limit orders.
  #   k - a non-negative number that will be interpreted as a percentage
  #
  # Returns:
  #   The largest amount of buy volume 
  
  book = book.sort(book)
  midprice1 <- book.midprice(book)
  midprice2 <- book.midprice(book)
  value <- -1
  if (nrow(book[[1]]) == 0){
    value <-0
  } else {
    for (j in 1:nrow(book[[1]])){
      while (midprice2 <= (midprice1 + (midprice1/100*k))){
        if (book[[1]][j,3] == 1){
          book[[1]] <- book[[1]][-j, ]
          value <- value + 1
          break;
        } else {
          book[[1]][j,3] <- book[[1]][j,3] - 1
          value <- value + 1
        }
      } 
      midprice2 <- book.midprice(book)
    }
  }
  return(value)
}