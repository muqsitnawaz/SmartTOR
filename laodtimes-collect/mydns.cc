#include <iostream>
#include <stdio.h> // basic I/O
#include <stdlib.h>
#include <sys/types.h> // standard system types
#include <netinet/in.h> // Internet address structures
#include <sys/socket.h> // socket API
#include <arpa/inet.h>
#include <netdb.h> // host to IP resolution
#include <string.h>
#include <unistd.h>

#define HOSTNAMELEN 40 // maximal host name length; can make it variable if you want
#define BUFLEN 1024 // maximum response size; can make it variable if you want

int main(int argc, char *argv[])
{
  // define your variables here

  // check that there are enough parameters
  if (argc != 2)
    {
      fprintf(stderr, "Usage: mydns <hostname>\n");
      exit(-1);
    }

  struct hostent *hostnet_structure;
  int i = 0;

  if (! (hostnet_structure = gethostbyname(argv[1]))) {
    printf("%s\n","Error: Invalid URL!");
    exit(1);
  }

  while ((hostnet_structure -> h_addr_list)[i] != 0) {
    std::cout << "Name: " << hostnet_structure -> h_name << std::endl;
    std::cout << "Address: " << inet_ntoa(* ((struct in_addr *) (hostnet_structure -> h_addr_list[i]))) << std::endl;
    i++;
  }

  return 0;
}
