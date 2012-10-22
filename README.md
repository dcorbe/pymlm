pymlm
=====

pymlm: The Python Mailing List Manager

Q: Why another mailing list manager?

pymlm is agnostic to its environment.  If you're like me, then your
MTA is built into your network with a fair amount of complexity.  If
that complexity happens to include a mailing list manager then C'est
le Vie; this software isn't for you.

On the other hand, if you've managed to get your MTA working as
desired but have come to find that your mailing list manager of choice
does not fit nicely in your environment, then pymlm is right for you.

Pymlm is an IMAP4 client which is capable of processing inbound
messages like a mailing list manager.  It does not need to be
''plugged in'' to an MTA and it works off the shelf with (almost) any
IMAP server.  

The initial version of pymlm is designed for minimalism.  It meant to
support public mailing lists in a fairly feature-limited package.  We
are open to suggestions, though.  We hope that this is useful to
someone.  

Q: So how do I use this thing?

Setting pymlm up for the first run:

1) Set up a generic IMAP mailbox for pymlm
2) Plug the IMAP and SMTP access details into lists.conf.default and
rename it to lists.conf
3) Configure your MTA so it delivers E-Mail for one or more E-Mail
addresses (your lists) to pymlm's IMAP INBOX folder.
4) Configure your lists using the pymlm command line:

Add a list: pymlm.py -n somelist@someplace.com -a owner@someplace.com
Add a subscriber to a list: pymlm.py -s somelist@someplace.com -a subscriber@sompleace.com
Remove a subscriber from a list: pymlm.py -s somelist@someplace.com -a subscriber@somplace.com

usage: pymlm.py [-h] -c <config> [-s <list>] [-u <list>] [-a <address>]
                [-n <list>]

optional arguments:
  -h, --help    show this help message and exit
  -c <config>   Path to config file
  -s <list>     In conjunction with -a, subscribe to <list>
  -u <list>     In conjunction with -a, unsubscribe to <list>
  -a <address>  E-Mail address
  -n <list>     Create list with -d(ecription, optional) -a (owned by,
                mandatory)

Pymlm also responds to various request address.  Chiefly:

somelist-subscribe@someplace.com:  Subscribe to a mailing list
somelist-unsubscribe@somplace.com: Unsubscribe from a mailing list

Q: Getting help, giving feedback, etc.

Of course, we eat our own dogfood.  If you're interested then please
join our development mailing list by sending a message to
pymlm-subscribe@corbe.net



