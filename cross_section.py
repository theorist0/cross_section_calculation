"""

# ACCORDING TO CERN VACUUM TECHNICAL NOTE 96-01 (1996) THE CROSS SECTIONS OF PARTICLES IN THE HIGH ENERGY REGIME
# ONLY DEPENDS ON THE ENERGY, NOT ON THE EXACT PARAMETERS (LIKE CHARGE). THUS  THE CROSS SECTION GENERATED BY
# 7TeV PROTONS IS EQUAL TO THE ONE OF 3.81GeV ELECTRONS. THUS AN ADAPTED VERSION OF THE BINARY ENCOUNTER BETHE
# VRIENS MODEL IS USED TO DETERMINE THE DIFFERENTIAL CROSS SECTION, self.w_max, WHOSE ANALYTICAL FORM CAN BE
# INTEGRATED AS BELOW, TO OBTAIN THE TOTAL CROSS SECTION.

Author :    Kyle Poland
Sources :   Binary-encounter-dipole model for electron-impact ionization
            ( https://journals.aps.org/pra/pdf/10.1103/PhysRevA.50.3954 )

"""

import numpy as np
from scipy.integrate import quad


class Atom(object):
    def __init__(self, Z, B, N, Ni, Mi, ai_below, ai_above, U_bed):
        """
        :param B:           Bound electron binding energy in eV w.r.t the shell
        :param N:           Total occupation number of requested atom w.r.t the shell
        :param Ni:          Values of Ni for requested atom, for each subshell
        :param Mi:          Values of Mi for requested atom, for each subshell
        :param ai_below:    Coefficients in a 7-th order fit for dipole oscillator strength for
                            energies below 2s ionization energy of (originally scaled via units of bounding energy)
        :param ai_above:    Coefficients in a 7-th order fit for dipole oscillator strength for
                            energies above 2s ionization energy of (originally scaled via units of bounding energy)
        :param U_bed:       Bound electron kinetic energy in eV in the BED model
        """
        self.Z = Z
        self.B = B
        self.N = N
        self.Ni = Ni
        self.Mi = Mi
        self.ai_below = ai_below
        self.ai_above = ai_above
        self.U_bed = U_bed


class AtomFactory(object):
    """
    Generate instances with atom properties
    """


    @staticmethod
    def get_hydrogen():
        Z = 1.
        B = np.array([(13.6057)])
        N = np.array([(1)])

        Ni = np.array([(0.4343)])
        Mi = np.array([(0.2834)])

        ai_below_2s_ion_threshold = np.array(
            [0.0, -2.2473e-2, 1.1775, -4.6264e-1, 8.9064e-2, 0.0, 0.0]
        )

        ai_above_2s_ion_threshold = np.array(
            [0.0, -2.2473e-2, 1.1775, -4.6264e-1, 8.9064e-2, 0.0, 0.0]
        )

        U_bed = np.array([(13.6057)])

        return Atom(
            Z, B, N, Ni, Mi, ai_below_2s_ion_threshold, ai_above_2s_ion_threshold, U_bed
        )


    @staticmethod
    def get_h2():
        Z = 2.
        B = np.array([(1.543e1)])
        N = np.array([(2)])

        Ni = np.array([1.173])
        Mi = np.array([0.68])

        ai_below_2s_ion_threshold = np.array(
            [0.0, 0.0, 1.1262, 6.3982, -7.8055, 2.144, 0.0]
        )

        ai_above_2s_ion_threshold = np.array(
            [0.0, 0.0, 1.1262, 6.3982, -7.8055, 2.144, 0.0]
        )

        U_bed = np.array([2.568e1])

        return Atom(
            Z, B, N, Ni, Mi, ai_below_2s_ion_threshold, ai_above_2s_ion_threshold, U_bed
        )


    @staticmethod
    def get_helium():
        Z = 2.
        B = np.array([(2.459e1)])
        N = np.array([(2)])

        Ni = np.array([(1.605)])
        Mi = np.array([(0.489)])

        ai_below_2s_ion_threshold = np.array(
            [0.0, 0.0, 1.2178e1, -2.9585e1, 3.1251e1, -1.2175e1, 0.0]
        )

        ai_above_2s_ion_threshold = np.array(
            [0.0, 0.0, 1.2178e1, -2.9585e1, 3.1251e1, -1.2175e1, 0.0]
        )

        U_bed = np.array([(3.951e1)])

        return Atom(
            Z, B, N, Ni, Mi, ai_below_2s_ion_threshold, ai_above_2s_ion_threshold, U_bed
        )


    @staticmethod
    def get_neon():
        Z = 10.
        B = np.array([21.7, 48.47, 866.9])
        N = np.array([6, 2, 2])

        Ni = np.array([6.963, 0.7056, 1.686])
        Mi = np.array([1.552, 4.8e-2, 1.642e-2])

        ai_below_2s_ion_threshold = np.array(
            [
                [4.8791, -2.882, -7.4711e-1, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.7769, 2.8135, -3.151e1, 6.3469e1, -5.2528e1, 1.5982e1],
                [0.0, 0.0, 5.2475, -2.8121, 0.0, 0.0, 0.0],
            ]
        )

        ai_above_2s_ion_threshold = np.array(
            [
                [0.0, -5.8514, 3.2930e2, -1.6788e3, 3.2985e3, -2.3250e3, 0.0],
                [0.0, 1.7769, 2.8135, -3.151e1, 6.3469e1, -5.2528e1, 1.5982e1],
                [0.0, 0.0, 5.2475, -2.8121, 0.0, 0.0, 0.0],
            ]
        )

        U_bed = np.array([1.1602e2, 1.4188e2, 1.2591e3])

        return Atom(
            Z, B, N, Ni, Mi, ai_below_2s_ion_threshold, ai_above_2s_ion_threshold, U_bed
        )




class CrossSectionCalc:
    m_e = 9.11e-31  # Electron mass in kg
    c = 3e8  # Speed of light in m/s
    a_0 = 5.29e-9  # Bohr radius in cm
    alpha = 1.0 / 137  # Fine structure constant
    R = 13.6  # Rydberg constant in eV

    def __init__(self, T, atom=AtomFactory.get_neon()):
        self.atom = atom
        self.T = (T) #* 1e9
        self.t = self.T / atom.B  # T in units of binding energy(vector with entries for each subshell)
        self.w_max = (self.t - (1)) / (2)
        self.u = self.atom.U_bed / self.atom.B  # Constant factor from derivation



class CrossSectionCalcBed(CrossSectionCalc):
    def __init__(self, T, atom=AtomFactory.get_neon()):
        CrossSectionCalc.__init__(self, T, atom)


    def calculate_modified_oscillator_strength(self, w, n_shell):
        """
        Example:
        >>> calc = CrossSectionCalcBed(3.81e9, atom = AtomFactory.get_neon())
        >>> w = calc.w_max[2]
        >>> calc.calculate_modified_oscillator_strength(w, 2)

        :param w:
        :param n_shell:
        :return:
        """
        threshold = ((w) + 1.0) * self.atom.B[n_shell]
        coefficient_matrix = (
            self.atom.ai_below if threshold < (48.47) else self.atom.ai_above
        )
        quotient = [1 / ((w) + (1.0)) ** i for i in range(1,8)]
        osc_str = np.reshape(np.dot(coefficient_matrix, np.array(quotient)), (len(self.atom.B)))
        return 1/(w + 1) * osc_str[n_shell]

    def calculate(self):
        """
        Example:

        >>> calc = calc = CrossSectionCalcBed(3.81e9, atom = AtomFactory.get_h2())
        >>> calc.calculate()
        :return:
        """
        integrated_cross_sec_subshells = np.zeros(len(self.w_max))
        for n_shell in range(len(self.w_max)):
            u = self.atom.U_bed[n_shell] / self.atom.B[n_shell]
            S = (
                (4)
                * (np.pi)
                * self.a_0 ** 2
                * self.atom.N[n_shell]
                * (self.R / self.atom.B[n_shell])**2
            )

            factor = S / (self.t[n_shell] + u + 1.0)

            sub_factor1_1 = 2.0 - (self.atom.Ni[n_shell] / self.atom.N[n_shell])
            sub_factor1_2 = (self.t[n_shell] - 1.0) / self.t[n_shell] - np.log(self.t[n_shell]) / (self.t[n_shell] + 1.)
            summand1 = sub_factor1_1 * sub_factor1_2

            integrated_cross_sec_subshells[n_shell] = quad(
                self.calculate_modified_oscillator_strength, 0, self.w_max[n_shell], args=(n_shell)
            )[0]

            integrated_cross_sec_subshells[n_shell] *= np.log(self.t[n_shell]) / self.atom.N[n_shell]
            integrated_cross_sec_subshells[n_shell] += summand1
            integrated_cross_sec_subshells[n_shell] *= factor

        total_cross_section_bed = np.sum(integrated_cross_sec_subshells)


        return (total_cross_section_bed)

    def bethe_asymptotic(self):
        """
        Example
        >>> bethe = CrossSectionCalcBed(1.4e7, atom=AtomFactory.get_helium())
        >>> bethe.bethe_asymptotic()
        """

        cross_section_vec = np.zeros(len(self.w_max))
        for n_shell in range(len(self.w_max)):
            S = (
                    (4)
                    * (np.pi)
                    * self.a_0 ** 2
                    * self.atom.N[n_shell]
                    * (self.R / self.atom.B[n_shell]) ** 2
            )
            Q = 2 * self.atom.B[n_shell] * self.atom.Mi[n_shell] / (self.atom.N[n_shell] * self.R)
            cross_section_vec[n_shell] = S * Q / 2 * np.log(self.t[n_shell]) / self.t[n_shell]
        cross_section_bethe = np.sum(cross_section_vec)
        return 1.0e4 * cross_section_bethe

    def Mi_calculation(self, lower_boundary, upper_boundary, n_shell):
        """
        Example:
        >>> calc = CrossSectionCalcBed(3.81e9,  atom = AtomFactory.get_neon())
        >>> calc.Mi_calculation(0., np.inf, 2)
        """
        Mi_n_shell = quad(self.calculate_modified_oscillator_strength, lower_boundary, upper_boundary, args=(n_shell)
            )[0]
        Mi_n_shell *= self.R / self.atom.B[n_shell]
        return Mi_n_shell


class CrossSectionCalcBeb(CrossSectionCalc):
    def __init__(self, T, atom = AtomFactory.get_neon()):
        CrossSectionCalc.__init__(self, T, atom)
        self.Q = 1. / 2


    def calculate(self):

        """
        Calculate ionization cross section acording to the BEB model, which is a simplified model of the BED ansatz
        >>> calcBeb = CrossSectionCalcBeb(3.81e9, atom = AtomFactory.get_hydrogen())
        >>> calcBed =  CrossSectionCalcBed(3.81e9, atom = AtomFactory.get_hydrogen())
        >>> calcBeb.calculate() - calcBed.calculate()
        :return:
        """

        integrated_cross_sec_subshells = np.zeros(len(self.w_max))
        for n_shell in range(len(self.w_max)):
            u = self.atom.U_bed[n_shell] / self.atom.B[n_shell]
            S = (
                    (4)
                    * (np.pi)
                    * self.a_0 ** 2
                    * self.atom.N[n_shell]
                    * (self.R / self.atom.B[n_shell]) ** 2
            )

            factor = S / (self.t[n_shell] + u + 1.0)

            sub_factor1_1 = self.Q / 2
            sub_factor1_2 = ( 1. - 1. / (self.t[n_shell]) ** 2 ) * np.log(self.t[n_shell])
            summand1 = sub_factor1_1 * sub_factor1_2

            sub_factor2_1 = 2.0 - self.Q
            sub_factor2_2 = (self.t[n_shell] - 1.0) / self.t[n_shell] - np.log(self.t[n_shell]) / (self.t[n_shell] + 1.)
            summand2= sub_factor2_1 * sub_factor2_2

            integrated_cross_sec_subshells[n_shell] += summand1 + summand2
            integrated_cross_sec_subshells[n_shell] *= factor

        total_cross_section_bed = np.sum(integrated_cross_sec_subshells)

        return (total_cross_section_bed)







class CrossSectionCalcBebvm(CrossSectionCalc):
    def __init__(self, T, atom=AtomFactory.get_neon()):
        CrossSectionCalc.__init__(self, T, atom)
        self.bbar = atom.B / (self.m_e * self.c ** 2)
        self.ubar = atom.U_bed / (self.m_e * self.c ** 2)
        self.beta_b = 1 - 1 / (1 + self.bbar) ** 2
        self.beta_u = 1 - 1 / (1 + self.ubar) ** 2
        self.tbar = self.T / (self.m_e * self.c ** 2)
        self.beta_t = 1 - 1 / (1 + self.tbar) ** 2
        array_elems = [np.log(elem) for elem in (self.beta_t / self.beta_b)]
        value = np.sqrt(
            self.alpha ** 2 / (self.beta_t + self.beta_b) * np.array(array_elems)
        )
        self.phi = np.cos(value)
        self.f_2 = (
            -self.phi / (self.t + 1) * (1 + 2 * self.tbar) / (1 + self.tbar / 2) ** 2
        )
        self.f_3 = (
            np.log(self.beta_t * (1 + self.tbar) ** 2)
            - self.beta_t
            - (2 * np.array([np.log(elem) for elem in self.bbar]))
        )

    '''
    def calculate(self):
        pass




    def total_cross_section_bebvm(self):

        """

        # INTEGRATED VERSION OF BEBVM INTEGRATED FROM A FINAL EJECTED KINETIC ENERGY OF 0 TO w_max = ( (T + U) / B - 1 ) / 2
        # TO OBTAIN TOTAL CROSS SECTION. ORIGINAL FORM OF THE DIFFERENTIAL CROSS SECTION:
        # d_sigma/d_w = f_1 * ( f_2 * (1 / (w + 1) + 1 / (t - w)) + 1 / (w + 1)**2 +
        # + 1 / (t - w)**2 + bbar**2 / (1 + tbar / 2)**2 + f_3 * (1 / (w + 1)**3 + 1 / (t - w)**3) )

        :return: Integrated cross section calculated with the BEBVM model

        """
        f_1 = (
            (4.0)
            * np.pi
            * self.alpha ** (4.0)
            * self.a_0 ** (2.0)
            * self.atom.N
            / ((2.0) * self.bbar * (self.beta_t + (self.beta_b + self.beta_u)) / (2.0))
        )
        total_cross_sec = np.sum(
            f_1
            * (
                self.f_2 * np.array([elem.ln() for elem in ((self.w_max + (1.0)) / (self.t - self.w_max) * self.t)])
                - (1) / (self.w_max + (1.0))
                + (1.0)
                + (1.0) / (self.t - self.w_max)
                - (1.0) / self.t
                + self.bbar ** 2 * self.w_max / ((1.) + self.tbar / (2.0)) ** 2
                + self.f_3
                / (2.0)
                * (
                    (1) / (self.t - self.w_max) ** 2
                    - (1) / self.t ** (2.0)
                    - (1) / (self.w_max + (1.0)) ** 2
                    + (1)
                )
            )
        )
        return (1.0e4) * (total_cross_sec)


    def differential_cross_section_subshells_bed(self, w_var, n_shell):
        w = (w_var)
        # Current kinetic energy of electrons in respective shell(n_shell) in units of the binding energy
        u = self.atom.U_bed[n_shell] / self.atom.B[n_shell]
        # different coefficients for different energy regimes, W+U-B hereby corresponds to the
        ai = (
            self.atom.ai_below
            if (w + u - (1.0)) * self.atom.B[n_shell] < (48.47)
            else self.atom.ai_above
        )
        osc_str_vec = np.dot(
            ai, np.array([-1 / (w + u - (1.0)) ** (i + 2) for i in range(7)])
        )

        osc_str = np.reshape(osc_str_vec, (len(self.atom.B)))[n_shell]

        # Vector with corresponding cross sections for ionization from every
        # subshell
        diff_cross_sec_subshell_n = self._calculate_diff_cross_sec_subshell_n(n_shell, u, w, osc_str)

        return diff_cross_sec_subshell_n

    def total_cross_section_bed(self):
        """
        Calculate the cross section binary encouter dipole

        Example:
        >>> calc = CrossSectionCalc(3810, atom= AtomFactory.get_neon())
        >>> calc.total_cross_section_bed()
        4.007883837878639e-18

        :return: Total integrated cross section
        """

        integrated_cross_sec_subshells = np.zeros(len(self.w_max))
        for i in range(len(self.w_max)):
            integrated_cross_sec_subshells[i] = quad(
                self.differential_cross_section_subshells_bed,
                (0.),
                self.w_max[i],
                args=(i),
            )[0]
        total_cross_section_bed = np.sum(integrated_cross_sec_subshells)

        return (1.0e4) * (total_cross_section_bed)  # Converting from m**2 to cm**2

def _calculate_diff_cross_sec_subshell_n(self, n_shell, u, w, osc_str):
        """
        Helper function to calculate the integral of my ass

        :param n_shell:
        :param u:
        :param w:
        :param osc_str:
        :return:
        """
        return (
                self.f_1_bed
                / (self.t + u + (1.0))
                * (
                        (self.atom.Ni / self.atom.N - (2.0))
                        / (self.t + (1.0))
                        * ((1.0) / (w + (1.0)) + (1.0) / (self.t - w))
                        + ((2.0) - self.atom.Ni / self.atom.N)
                        * ((1.0) / (self.t - w) ** 2 + (1.0) / (w + (1.0)) ** 2)
                        + np.array([elem.ln() for elem in self.t]) / self.atom.N
                        * np.dot((1.0) / (w + (1.0)), osc_str)
                )
        )[n_shell]

    def integ(self, a, b, n_sample, shell = 0):
        x_vals = np.linspace(a, b, num = n_sample)
        dx = ((b) - (a)) / (n_sample)
        integral = (0)
        for x in x_vals:
            integral += ((x))**2 * dx #self.differential_cross_section_subshells_bed(x, shell) * dx
        return integral

    def integ2(self, a, b, dx_initial, shell = 0):
        dx = (dx_initial)
        x = (a)
        integral = (0)
        while x <= b:
            delta_integral = (x + dx / 2)**2 * dx  #self.differential_cross_section_subshells_bed(x, shell) * dx
            integral += delta_integral
            dx /= delta_integral
            x += dx
        return integral

    '''
