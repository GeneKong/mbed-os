import re

from os.path import join, exists, dirname
from os import makedirs

from tools.export.makefile import Makefile, GccArm, Armc5, IAR

class Eclipse(Makefile):
    """Generic Eclipse project. Intended to be subclassed by classes that
    specify a type of Makefile.
    """
    def generate(self):
        """Generate Makefile, .cproject & .project Eclipse project file,
        py_ocd_settings launch file, and software link .p2f file
        """
        super(Eclipse, self).generate()
        starting_dot = re.compile(r'(^[.]/|^[.]$)')
        ctx = {
            'name': self.project_name,
            'elf_location': join('BUILD',self.project_name)+'.elf',
            'c_symbols': self.toolchain.get_symbols() + self.GLOBAL_SYMBOLS,
            'asm_symbols': self.toolchain.get_symbols(True) + self.GLOBAL_SYMBOLS,
            'target': self.target,
            'include_paths': [starting_dot.sub('../../../', inc) for inc in self.resources.inc_dirs],
            'load_exe': str(self.LOAD_EXE).lower()
        }       

        if not exists(join(self.export_dir,'eclipse-extras')):
            makedirs(join(self.export_dir,'eclipse-extras'))


        self.gen_file('cdt/pyocd_settings.tmpl', ctx,
                      join('eclipse-extras',
                           '{target}_pyocd_{project}_settings.launch'.format(target=self.target,
                                                                             project=self.project_name)))
        self.gen_file('cdt/necessary_software.tmpl', ctx,
                      join('eclipse-extras','necessary_software.p2f'))

        ctx['files'] = []
        for file in self.resources.c_sources:
            ctx['files'].append(file.strip('./'))
        for file in self.resources.cpp_sources:
            ctx['files'].append(file.strip('./'))
        for file in self.resources.s_sources:
            ctx['files'].append(file.strip('./'))

        for flag in self.toolchain.asm[1:]:
            if flag.startswith('-D'):
                ctx['asm_symbols'].append(flag[2:])

        for flag in self.toolchain.cc[1:]:
            if flag.startswith('-D'):
                ctx['c_symbols'].append(flag[2:])

        for flag in self.toolchain.cppc[1:]:
            if flag.startswith('-D'):
                ctx['c_symbols'].append(flag[2:])

        ctx['gnu_inc'] = dirname(self.toolchain.cc[0])
        self.gen_file('cdt/.cproject.tmpl', ctx, '.cproject')
        self.gen_file('cdt/.project.tmpl', ctx, '.project')


class EclipseGcc(Eclipse, GccArm):
    LOAD_EXE = True
    NAME = "Eclipse-GCC-ARM"
    GLOBAL_SYMBOLS = [  "__GNUC__",
                        "___int8_t_defined",
                        "___int16_t_defined",
                        "___int32_t_defined",
                        "___int64_t_defined",
                        "NULL=0"
                        ]

class EclipseArmc5(Eclipse, Armc5):
    LOAD_EXE = False
    NAME = "Eclipse-Armc5"
    GLOBAL_SYMBOLS = ["__CC_ARM"]

class EclipseIAR(Eclipse, IAR):
    LOAD_EXE = True
    NAME = "Eclipse-IAR"
    GLOBAL_SYMBOLS = ["__ICCARM__"]


