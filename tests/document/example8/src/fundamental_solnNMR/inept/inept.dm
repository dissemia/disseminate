---
chapter: INEPT and Signal Enhancement
author: Justin Lorieau
targets: html, tex, pdf
@T1: T@sub{1}
@p90: 90@deg
@p180: 180@deg
@p90x: 90@supsub{○ && x}
@p180x: 180@supsub{○ && x}
@p90x1H: @p90x (@1H)
@p180x1H: @p180x (@1H)
@p180xX: @p180x (X)
@CSh: @omega@sub{H}
@Jnh: J@sub{NH}
@CcsD: @term[color=blue]{C_{CS@Delta}}
@CjD : @term[color=blue]{C_{@Jnh @Delta}}
@ScsD: @term[color=red!80!black]{S_{CS@Delta}}
@SjD : @term[color=red!80!black]{S_{@Jnh @Delta}}
@eqbreak: \displaybreak[2] \\[0.5em]
---

@chapter
@author{}

The purpose of the @abrv{INEPT} sequence@cite{Morris1979} is to
transfer the large magnetization from high-@gamma nuclei, like @sup{1}H or
@19F, to low-@gamma nuclei (labeled 'X'), like @13C and @15N. This transfer
significantly improves the signal intensity of 'X' nuclei when
measuring their chemical shifts. For example, the magnetic moment and
magnetization of @1H nuclei is roughly 4 times greater than @13C and 10
times greater than @15N. Additionally, the @1H @T1 is typically much
shorter than the @T1 for @13C or @15N, which allows a shorter recycle
delay and the collection of a greater number of spectra.

@section{Theory}

@marginfig[id=fig:inept-inept1]{
  @asy[scale=1.0]{
  size(200);
  draw(unitcircle);  
  }
  @caption{The basic @abrv{INEPT} sequence between nuclei @1H
    and X.}
}

The @abrv{INEPT} sequence (@ref{fig:inept-inept1}) transfers
magnetization from @1H nuclei bonded the 'X' nuclei. The two
nuclei must be bonded, or at least connected through intermediary
bonds with other atoms, because the nuclei must share a J-coupling.

The @abrv{INEPT} sequence comprises a set of @p90 pulses (thin bars),
@p180 pulses (thick bars) and delays (@Delta).

@subsection{Methine, Amide and the AX Spin Systems}

The first @p90x1H pulse creates @termb{-H_y} @1H magnetization.
@sidenote{A @p90x pulse rotates the magnetization by @p90 with a phase
of 'x'.}  Thereafter, the @1H @p180 pulse in the middle of the two
@Delta delays acts as a Hahn-echo to refocus the @1H chemical
shifts. Without the accompanying @p180 pulse on the 'X' channel, the
J-coupling between the @1H and X nucleus would be refocused as
well---and nothing would be accomplished. The @p180 pulse on the 'X'
channel acts to @i{cancel} the refocusing effect of the @1H @p180
pulse for the J-coupling.

During the first delta period, the @termb{- H_y} magnetization evolves
under the @1H chemical shift (@CSh) and the @1H-X
J-coupling. Since the chemical shift and J-coupling Hamiltonians
commute, the rotations of each can be conducted sequentially.

In the first step, the operators are propagated for the @p90x1H pulse
and the first '@Delta' period. We'll use a @15N nucleus as an example
of an 'X' nucleus.

@eq[env=alignat* 3]{
  @termb{H_z} & \xrightarrow{\mathmakebox[3em]{@p90x1H}} && @termb{- H_y} \\
  @termb{-H_y}& \xrightarrow{\mathmakebox[3em]{@CSh@Delta}} &&
    @termb{-H_y} \cos(@CSh @Delta) + @termb{H_x} \sin(@CSh @Delta) \\
  & \xrightarrow{\mathmakebox[3em]{@Jnh @Delta}} &&
  @termb{-H_y} \cos(@CSh @Delta) \cos(\pi @Jnh @Delta) + \\
   & &&
  \quad @termb{2H_x N_z} \cos(@CSh @Delta) \sin(\pi @Jnh @Delta) + \\
   & &&
  \quad @termb{H_x} \sin(@CSh @Delta) \cos(\pi @Jnh @Delta) + \\
   & &&
  \quad @termb{2H_y N_z} \sin(@CSh @Delta) \sin(\pi @Jnh @Delta)
 }

