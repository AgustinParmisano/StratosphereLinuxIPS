#!/usr/bin/python -u
# This file is part of the Stratosphere Linux IPS
# See the file 'LICENSE' for copying permission.
#Author: Ondrej Lukas - ondrej.lukas95@gmail.com, lukasond@fel.cvut.cz

import signal
import time
import sys

class SignalHandler(object):
    def __init__(self,process):
            self.process = process

    def register_signal(self, signal_n):
            signal.signal(signal_n,self.process_signal)

    def process_signal(self,signal, frame):
        #print "signal:{},frame:{},time:{}.".format(signal,frame,datetime.now())
        try:
            print "\nInterupting SLIPS"
            self.process.ip_handler.print_alerts()
            time.sleep(0.5)
        except Exception:
            print "Sth went wrong"
        #self.process.stop()
        self.process.terminate()
        time.sleep(1)
        sys.exit(0)

class WhoisHandler(object):
    def __init__(self,whois_file):
        self.whois_data = {}
        self.filename = whois_file
        try:
            with open(whois_file) as f:
                for line in f:
                    # What about repetitions?
                    try:
                        (key,val) = line.strip().split("___")
                        self.whois_data[key] = val
                    except ValueError:
                        # A probable malformed line. Ignore
                        pass
        except IOError:
            print "Whois informaton file:'{}' doesn't exist!".format(self.filename)
            pass
    
    def get_whois_data(self,ip):
        #do we have it in the cache?
        try:
            import ipwhois
        except ImportError:
            print 'The ipwhois library is not install. pip install ipwhois'
            return False
        # is the ip in the cache
        try:
            desc = self.whois_data[ip]
            return desc
        except KeyError:
            # Is not, so just ask for it
            try:
                obj = ipwhois.IPWhois(ip)
                data = obj.lookup_whois()
                try:
                    desc = data['nets'][0]['description'].strip().replace('\n',' ') + ',' + data['nets'][0]['country']
                except AttributeError:
                    # There is no description field
                    desc = ""
            except ValueError:
                # Not a real IP, maybe a MAC
                desc = 'Not an IP'
                pass
            except IndexError:
                # Some problem with the whois info. Continue
                desc = ""
                pass        
            except ipwhois.IPDefinedError as e:
                if 'Multicast' in e:
                    desc = 'Multicast'
                desc = 'Private Use'
            # Store in the cache
            self.whois_data[ip] = desc
            return desc
        except Exception as inst:
            print '\tProblem with get_whois_data() in utils.py'
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly
            sys.exit(1)


    def store_whois_data_in_file(self):
        """ TODO: Description"""
        f = open(self.filename,"w")
        for item in self.whois_data.items():
            f.write('{}___{}\n'.format(item[0],item[1]));
        f.close();






