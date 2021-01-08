import sys
from .enums import VMResult
from .error_machinery import ErrorMachinery
from . import vm


errmac = ErrorMachinery()


class Plox:
    def __init__(self):
        self.vm = vm.VM()

    def run(self, source):
        self.vm.init()
        return self.vm.interpret(source)

    def run_oneshot(self, source):
        out = self.run(source)
        if out is VMResult.COMPILE_ERROR:
            sys.exit(65)
        elif out is VMResult.RUNTIME_ERROR:
            sys.exit(70)

        return out

    def run_interactive(self, source):
        result = self.run(source)
        errmac.reset()
        return result

    def run_file(self, filename):
        with open(filename, encoding="utf8") as f:
            out = self.run_oneshot(f.read())
            if out:
                print(out)

    def repl(self):
        while True:
            try:
                source = input("% ")
            except (KeyboardInterrupt, EOFError) as e:
                print(e.__class__.__name__)
                sys.exit(0)

            if source:
                try:
                    out = self.run_interactive(source)
                except KeyboardInterrupt:
                    print("KeyboardInterrupt")
                else:
                    if out:
                        print(out)
                finally:
                    pass

