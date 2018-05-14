#
# Copyright (c) 2012 Daniel Corbe <pymlm@corbe.net>
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the authors, copyright holders or the contributors
#    may be used to endorese or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS, AUTHORS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE COPYRIGHT HOLDERS, AUTHORS OR CONTRIBUTORS BE HELD LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, COPYRIGHT ENFRINGEMENT, LOSS
# OF PROFITS, REVENUE, OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import email, imaplib, smtplib, re, sys, argparse, string, random, textwrap
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

class MLM():
    def __init__(self, config):
        self.config = SafeConfigParser()
        self.config.read(config)
        self.configfile = config

    def list_isvalid(self, address):
        if self.config.has_section(address.lower()):
            return True
        else:
            return False

    def bounce_nolist(self, msg):
        print "Bouncing E-Mail to unknown list: {0}".format(msg.get("To"))


    def process_msg(self, msg, to):
        print "Processing new E-Mail for list: {0}".format(to)
    
        # Extract the user and host portions of the list address. 
        user, host = to.split('@')

        # We need to know what the MTA's delimiter is
        delimiter = self.config.get('general', 'delimiter')

        #
        # Add necessary headers to the E-Mail message
        #
        msg.add_header('List-Id', self.config.get(to.lower() , 'listid'))
        msg.add_header('List-Help', 
                       '{0}-help@{1}'.format(user, host))
        msg.add_header('List-Subscribe',
                       '{0}-subscribe@{1}'.format(user, host))
        msg.add_header('List-Unsubscribe',
                       '{0}-unsubscribe@{1}'.format(user, host))
        msg.add_header('List-Post',
                       '{0}@{1}'.format(user, host))
        msg.add_header('List-Owner',
                       self.config.get(to.lower(), 'owner'))

        try:
            replyto = self.config.get(to, reply-to)
        except:
            replyto = None

        if replyto:
            msg.add_header('Reply-To', replyto)

        # Relay the message to all the list subscribers
        try:
            mirror = self.config.get(to.lower(), 'mirror')
            subscribers = self.config.get(mirror.lower(), 'subscribers').split(', ')
        except:
            subscribers = self.config.get(to.lower(), 'subscribers').split(', ')
            
        for subscriber in subscribers:
            print "\tForwarding E-Mail to: {0}".format(subscriber)
            smtp = smtplib.SMTP(self.config.get('general', 'smtp_server'))

            try:
                forcefrom = self.config.get(to.lower(), 'from')
            except:
                forcefrom = to
                
            smtp.sendmail(forcefrom, subscriber, msg.as_string())

    def add_moderator(self, listaddr, address):
        #
        # First check to see if the list exists
        #
        try:
            moderators = self.config.get(listaddr, 'moderators').split(', ')
        except NoSectionError:
            raise NameError('Requested list does not exist: {0}'.format(listaddr))
        except NoOptionError:
            self.config.set(listaddr, 'moderators', address)
            f = open(self.configfile, 'w')
            f.truncate()
            self.config.write(f)
            f.close()
            return True

        #
        # Check to see if the subscriber is already on the list
        #
        for moderator in moderators:
            if moderator == address:
                raise ValueError('User {0] already moderator on {1}'.format(
                        address, listaddr))

        #
        # All good.  Reconstruct the moderatorss field and save the config
        #
        moderators.append(address)
        self.config.set(listaddr, 'moderators', ', '.join(moderators))
        f = open(self.configfile, 'w')
        f.truncate()
        self.config.write(f)
        f.close()
        return True

    def rm_moderator(self, listaddr, address):
        #
        # First check to see if the list exists
        #
        try:
            moderators = self.config.get(listaddr, 'moderators').split(', ')
        except NoSectionError:
            raise NameError('Requested list does not exist: {0}'.format(listaddr))
        except NoOptionError:
            self.config.set(listaddr, 'moderators', '')
            moderators = self.config.get(listaddr, 'moderators').split(', ')
        
        #
        # Check to see if the subscriber is already on the list
        #
        for moderator in moderators:
            if moderator == address:
                moderators.remove(moderator)
                self.config.set(listaddr, 'moderators', ', '.join(moderators))
                f = open(self.configfile, 'w')
                f.truncate()
                self.config.write(f)
                f.close()
                return True

        raise ValueError('User {0} is not a moderator on {1}'.format(
                address, listaddr))

    def is_moderator(self, listaddr, address):
        #
        # First check to see if the list exists
        #
        try:
            moderators = self.config.get(listaddr, 'moderators').split(', ')
        except NoSectionError:
            raise NameError('Requested list does not exist: {0}'.format(listaddr))
        except NoOptionError:
            return False
        
        #
        # Check to see if the subscriber is already on the list
        #
        for moderator in moderators:
            if moderator == address:
                return True

        return False

    def add_subscriber(self, listaddr, address):
        #
        # First check to see if the list exists
        #
        try:
            subscribers = self.config.get(listaddr, 'subscribers').split(', ')
        except NoSectionError:
            raise NameError('Requested list does not exist: {0}'.format(listaddr))

        #
        # Check to see if the subscriber is already on the list
        #
        for subscriber in subscribers:
            if subscriber == address:
                raise ValueError('User {0] already subscribed to {1}'.format(
                        address, listaddr))

        #
        # All good.  Reconstruct the subscribers field and save the config
        #
        subscribers.append(address)
        self.config.set(listaddr, 'subscribers', ', '.join(subscribers))
        f = open(self.configfile, 'w')
        f.truncate()
        self.config.write(f)
        f.close()
        return True

    def rm_subscriber(self, listaddr, address):
        #
        # First check to see if the list exists
        #
        try:
            subscribers = self.config.get(listaddr, 'subscribers').split(', ')
        except NoSectionError:
            raise NameError('Requested list does not exist: {0}'.format(listaddr))
        
        #
        # Check to see if the subscriber is already on the list
        #
        for subscriber in subscribers:
            if subscriber == address:
                subscribers.remove(subscriber)
                self.config.set(listaddr, 'subscribers', ', '.join(subscribers))
                f = open(self.configfile, 'w')
                f.truncate()
                self.config.write(f)
                f.close()
                return True

        raise ValueError('User {0} is not subscribed to {1}'.format(
                address, listaddr))

    def add_list(self, listaddr, owner, description=None, moderated=None):
        try:
            subscribers = self.config.get(listaddr, 'subscribers').split(', ')
            raise NameError('List already exists')
        except NoSectionError:
            pass

        user, host = listaddr.split('@')

        # If we get here, all good.
        subscribers = [ ]
        self.config.add_section(listaddr)
        self.config.set(listaddr, 'owner', owner)
        if description:
            self.config.set(listaddr, 'listid', description + ' <' +
                            self.gen_listid() +
                            '.pymlm.' +
                            host + '>')
        else:
            self.config.set(listaddr, 'listid', '<' +
                            self.gen_listid() +
                            '.pymlm.' +
                            host + '>')
        self.config.set(listaddr, 'subscribers', owner)

        if moderated:
            self.config.set(listaddr, 'moderated', 'true')

        # Write config to disk
        f = open(self.configfile, 'w')
        f.truncate()
        self.config.write(f)
        f.close()
        return True

    def rm_list(self, listaddr):
        try:
            subscribers = self.config.get(listaddr, 'subscribers').split(', ')
        except NoSectionError:
            raise NameError('List does not exist')

        config.remove_section(listaddr)
        # Write config to disk
        f = open(self.configfile, 'w')
        f.truncate()
        self.config.write(f)
        f.close()
        return True
            
    def gen_listid(self, size=8, 
                   chars=string.ascii_uppercase + 
                   string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def crawl_imap(self):    
        # Step one: Open INBOX
        mail = imaplib.IMAP4(self.config.get('general', 'imap_server'), self.config.get('general', 'imap_port'))
        mail.login(self.config.get('general', 'imap_user'), self.config.get('general', 'imap_pass'))
        mail.select()

        # Step two: Request a list of unread messages
        #result, messages = mail.search(None, "ALL")
        result, messages = mail.search(None, "UNSEEN")

        # Step three: Process unread messages (FIXME: Far too monolithic)
        for i in messages[0].split():
            r = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
            rawmsg = mail.fetch(i, "(RFC822)")
            msg = email.message_from_string(rawmsg[1][0][1])
            matched = False
            
            #
            # If this message is addressed to one of the -request
            # aliases, we need to apply special processing.
            #
            # FIXME we only support the first To: address for processing requests
            try:
                to = r.findall(msg.get("To"))[0]
                user, host = to.split('@')
            except:
                continue

            try:
                user, request = user.split(self.config.get('general', 'delimiter'))
            except ValueError:
                request = None

            if request:
                # Stops the while loop below from running
                # without ceasing execution entirely so that
                # cleanup (like expunging messages) can still
                # happen later.
                matched = True

                ofrom = r.findall(msg.get("From"))[0]

                if request == 'subscribe':
                    # FIXME: Shouldn't we add list headers here?
                    reply = textwrap.dedent('''\
                        From: {1}-request@{2}
                        To: {3}
                        Reply-To: {1}-unsubscribe@{2}
                        Subject: Subscribe {1}@{2}

                        Dear User,
                        
                        This is the mailing list manager running at {0}.
                        You (or possibly someone else) has requested a
                        subscription to the {1}@{2} mailing list which is managed
                        here.  If you did not initiate this request, please
                        reply to this message to have yourself removed from
                        this mailing list immediately.  If you did initiate
                        this request, then no further action on your part is
                        necessary.'''.format(host, user, host, ofrom))

                    smtp = smtplib.SMTP(self.config.get('general', 'smtp_server'))
                    smtp.sendmail('{0}-request@{1}'.format(user, host), 
                                  '{0}'.format(ofrom), 
                                  reply)
                    try:
                        self.add_subscriber('{0}@{1}'.format(user, host),
                                            ofrom)
                    except:
                        pass

                if request == 'unsubscribe':
                    # FIXME: Shouldn't we add list headers here?
                    reply = textwrap.dedent('''\
                        From: {1}-request@{2}
                        To: {3}
                        Reply-To: {1}-subscribe@{2}
                        Subject: Unsubscribe {1}@{2}

                        Dear User,
                        
                        This is the mailing list manager running at {0}.
                        You (or possibly someone else) has requested 
                        unsubscription from the {1}@{2} mailing list which 
                        is managed here.  If you did not initiate this request, 
                        please reply to this message to have yourself added back
                        to this mailing list immediately.  If you did initiate
                        this request, then no further action on your part is
                        necessary.'''.format(host, user, host, ofrom))

                    smtp = smtplib.SMTP(self.config.get('general', 'smtp_server'))
                    smtp.sendmail('{0}-request@{1}'.format(user, host), 
                                  '{0}'.format(ofrom), 
                                  reply)
                    try:
                        self.rm_subscriber('{0}@{1}'.format(user, host),
                                           ofrom)
                    except:
                        pass

            #
            # Process new, unread and list-bound messages
            #
            # This would be alot cleaner if the Python people weren't
            # so allergic to GOTO.  C'est la vie I suppose.
            #

            # Try determining the list address from the To: header
            # which may contain multiple addresses, so we need to Iterate.
            try:
                for to in r.findall(msg.get("To")):
                    if self.list_isvalid(to):
                        matched = True
                        if not request:
                            self.process_msg(msg, to)
                            continue
            except TypeError:
                pass

            # If the To: header is no mas, try searching the Cc: header
            try:
                for to in r.findall(msg.get("Cc")):
                    if self.list_isvalid(to):
                        matched = True
                        if not request:
                            self.process_msg(msg, to)
                            continue
            except TypeError:
                pass

            # If that fails then fall back to the X-Original-To header.
            # if not matched:
            #     to = msg.get("X-Original-To")
            #     if not matched and self.list_isvalid(to):
            #         matched = True
            #         #self.process_msg(msg, to)

            # Finally give up and bounce the message
            if not matched:
                self.bounce_nolist(msg)
                break

            # List processing.
            #if matched and not request:
                # TODO: FIXME
                # try:
                #     moderated = self.config.get(to.lower() , 'moderated')
                # except:
                #     moderated = "false"

                # if moderated == "true":

                #     # Check to see if the mail is from a list moderator
                #     processed = 0
                #     for mailfrom in r.findall(msg.get('From')):
                #         if self.is_moderator(to, mailfrom):
                #             processed = 1
                #             self.process_msg(msg, to)
                    
                #     # 
                #     # A reply to an existing message.  Process.
                #     #
                #     # FIXME: what the fuck.
                #     #
                #     if not processed:
                #         lreply = msg.get('In-Reply-To')
                #         if lreply:
                #             for stupid in r.findall(lreply):
                #                 if stupid:
                #                     processed = 1
                #                     self.process_msg(msg, to)
                            
                    # Not a moderator or a reply, bounce.
                    # if not processed:
                    #     ofrom = r.findall(msg.get("From"))[0]
                    #     reply = textwrap.dedent('''\
                    #     From: {1}-request@{2}
                    #     To: {3}
                    #     Reply-To: {1}-subscribe@{2}
                    #     Subject: Your E-Mail to {1}@{2}

                    #     Dear User,
                        
		    #     You attempted to send an E-Mail to a moderated list.
		    #     Your E-Mail has not been delivered.  For help please
		    #     contact the list owner.
                    #     necessary.'''.format(host, user, host, ofrom))

                    #     smtp = smtplib.SMTP(self.config.get('general', 'smtp_server'))
                    #     smtp.sendmail('{0}-request@{1}'.format(user, host), 
                    #               '{0}'.format(ofrom), 
                    #               reply)

        # Step four: expunge processed messages
        expunge = self.config.get('general', 'expunge')
        if expunge == "true":
            for i in messages[0].split():
                mail.store(i, '+FLAGS', '\\Deleted')
            mail.expunge()

        # Step five: close INBOX
        mail.close()
        mail.logout()
        
if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', 
                        required=True, 
                        metavar='<config>', 
                        help='Path to config file')
    parser.add_argument('-s',
                        metavar='<list>',
                        help='In conjunction with -a, subscribe to <list>')
    parser.add_argument('-u',
                        metavar='<list>',
                        help='In conjunction with -a, unsubscribe to <list>')
    parser.add_argument('-a',
                        metavar='<address>',
                        help='E-Mail address')
    parser.add_argument('-n',
                        metavar='<list>',
                        help='Create list with -d(ecription, optional) -a (owned by, mandatory)')
    parser.add_argument('-d',
                        metavar='<description>',
                        help='List Description')
    parser.add_argument('-m', action='store_true',
                        help='List should be moderated')
    parser.add_argument('-r',
                        metavar='<moderator>',
                        help='Remove moderator from list')
    parser.add_argument('-e',
                        metavar='<moderator>',
                        help='Add moderator to list')
    parser.add_argument('-l',
                        metavar='<list>',
                        help='Moderator management for <list>')
    args = parser.parse_args()

    mlm = MLM(args.c)

    if args.m:
        if not args.n:
            print "-m option only available on new lists"
            raise ValueError()

    if args.u:
        if not args.a:
            print "Must supply the -a(ddress) argument with -u"
            raise ValueError()

        mlm.rm_subscriber(args.u, args.a)
        sys.exit()

    if args.s:
        if not args.a:
            print "Must supply the -a(ddress) argument with -s"
            raise ValueError()

        mlm.add_subscriber(args.s, args.a)
        sys.exit()

    if args.n:
        if not args.a:
            print "Must supply the -a(ddress) argument with -s"
            raise ValueError()

        mlm.add_list(args.n, args.a, args.d, args.m)
        sys.exit()

    if args.r:
        if not args.l:
            print "Must supply a list (-l) to manage moderators"
            raise ValueError()

        mlm.rm_moderator(args.l, args.r)
        sys.exit()

    if args.e:
        if not args.l:
            print "Must supply a list (-l) to manage moderators"
            raise ValueError()

        mlm.add_moderator(args.l, args.e)
        sys.exit()

    mlm.crawl_imap()
