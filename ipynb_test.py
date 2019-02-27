###################################################################
#                                                                 #
#      Test Case Library for IPython Kernel Jupyter Notebook      #
#                           Allen Jiang                           #
#                                                                 #
#                                                     13 Feb 2019 #
###################################################################

import sys
from time import time
from IPython.display import display, Markdown

'''
Interface
'''
class ITestGroup:
    def run(self):
        pass


'''
Unit Test for Function
'''

class UnitTest (ITestGroup):
    
    def __init__(self, func, name=None):
        self.func = func
        self.cases = []
        self.results = []
        self.timer = Timer()
        self.name = name if name is not None else "unit test for {}".format(func.__name__)
        
    def run(self, report_type='md', verbose=True):
        self.__exec_cases__(verbose)
        self.__gen_report__(type=report_type)
        
    '''
    Adding test cases
    '''
    __cmp_eq__ = lambda a, b: a == b
    __cmp_typematch__ = lambda a, b: type(a) == type(b)
    
    def match(self, args, expected, criteria=__cmp_eq__):
        self.__add__(args, expected, criteria, expected_except=False)
        
        
    def exception(self, args, exception, criteria=__cmp_typematch__):
        self.__add__(args, exception, criteria, expected_except=True)
        
    
    def __add__(self, args, expected, criteria, expected_except):
        if not isinstance(args, list):
            raise TypeError(
                "Expected argument 'args' to be instance of list. \
                Given: {}".format(args))
            return
        if expected_except and not isinstance(expected, Exception):
            raise TypeError(
                "Expected argument 'expected' to be instance of Exception. \
                Given: {}".format(args))
            return
            
        self.cases.append((args, expected, expected_except, criteria))
        
    '''
    Execution of test cases
    '''
    def __exec_cases__(self, verbose=True):
        results = []
        
        # run all test cases
        for case in self.cases:
            args, expected, expected_except, criteria = case
            output, output_except, success = None, False, False

            # execute test
            try:
                self.timer.start()
                output = self.func(*args)
                self.timer.stop()
            except Exception as e:
                self.timer.stop()
                output_except = True
                output = e
                if not expected_except:
                    self.__exec_cases_runtime_stderr__(e, args)
                    if verbose:
                        raise
                        
            exec_time = self.timer.elapsed_ms()

            # test success
            success = criteria(output, expected)
            
            # write result
            results.append([
                args,
                (output, output_except),
                (expected, expected_except),
                success,
                exec_time
            ])

        self.results = results

    def __exec_cases_runtime_stderr__(self, e, args):
        str_args = ', '.join(map(repr, args))
        sys.stderr.write(
            'Unexpected exception {} during execution of {}({}):\n'.format(
                e.__class__.__name__,
                self.func.__name__,
                str_args
            ))
        
    '''
    Generation of reports
    '''
    
    def __gen_report__(self, type):
        if type == 'md':
            self.__gen_report_md__()
        else:
            raise ValueError("Invalid report type '{}'.".format(type))
            
            
    # markdown
    
    __md_code_format__ = lambda code : '`{}`'.format(repr(code))
    __md_colorize__ = lambda msg, clr: '<span style="color:{}">{}</span>'.format(clr, msg)
    
    def __gen_report_md__(self):
        ## Generate markdown
        md_str = ''

        # display empty set of results
        if len(self.results) == 0:
            md_str = 'no test case results for {}.'.format(
                self.func.__name__
            )
        # display non-empty set of results    
        else:
            # generate markdown report title
            md_str = '### {}:'.format(self.name)
            
            # break
            md_str += '\n\n'
            
            # generate markdown table header
            md_str += '| Arguments | Output | Expected | ✓ | ms |\n'
            md_str += '| :-------- | :----- | :------- | -- | -- |\n'

            # populate table rows
            for result in self.results:
                args, output, expected, success, exec_time = result
                # unpack exception states
                output, output_except = output
                expected, expected_except = expected
                
                display_row = []

                # args
                args = ', '.join(map(UnitTest.__md_code_format__, args))
                display_row.append(args)

                # output
                if output_except:
                    output = UnitTest.__md_colorize__(repr(output), 'red')
                else:
                    output = UnitTest.__md_code_format__(output)
                display_row.append(output)

                # expected
                if expected_except:
                    expected = UnitTest.__md_colorize__(repr(expected), 'red')
                else:
                    expected = UnitTest.__md_code_format__(expected)
                display_row.append(expected)

                # success (HTML5 coloring)
                if success:
                    display_row.append(UnitTest.__md_colorize__('*ok*', 'green'))
                else:
                    display_row.append(UnitTest.__md_colorize__('***fail***', 'red'))
                    
                # execution time
                display_row.append(UnitTest.__md_colorize__('{:01.2f}'.format(exec_time), 'lightgray'))

                # compile row
                md_str +=  "| {} |\n".format(' | '.join(display_row))

        # display markdown
        display(Markdown(md_str))
        
        
class Timer:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        
    def start(self):
        self.start_time = time()
        
    def stop(self):
        self.end_time = time()
    
    def elapsed_ms(self):
        return 1000 * (self.end_time - self.start_time)
        
        
def approxer(error):
    return lambda a, b: abs(a - b) <= error

# eof

