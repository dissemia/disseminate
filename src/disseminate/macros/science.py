"""
Macros for science.
"""

# spin active isotopes
macros_isotopes = {'@1H': '@sup{1}H',
                   '@2H': '@sup{2}H',
                   '@13C': '@sup{13}C',
                   '@15N': '@sup{15}N',
                   '@19F': '@sup{19}F',
                   '@31P': '@sup{31}P',
                   }

# Chemicals
macros_chemicals = {'@H2O': 'H@sub{2}O',
                    }

# Symbols
# Note: The degree symbol is a superscript circle instead of a degree character
# so that the @supsub tag can draw a degree symbol and the formatting is
# consistent.
macros_symbols = {'@deg': '@sup{○}',
                  }

# Greek Symbols
macros_greek = {'@' + i: '@symbol{' + i + '}'
                for i in ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta',
                          'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu',
                          'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau',
                          'upsilon', 'phi', 'chi', 'psi', 'omega',
                          'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta',
                          'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu',
                          'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau',
                          'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',)}
