#!/bin/env python

# Author: Rafael Lopes de Sa
# Date: A moment of boredom

# This is to read XML output (LHE files)
import xml.etree.ElementTree as ET

# ROOT interface
import ROOT

# To check if the file exists
import os

def readFiles(eventFiles):

    ''' This is just to concatenate many MadGraph runs '''

    events = []
    for LHEFile in eventFiles:
        events = events + getEvents(LHEFile, float(len(eventFiles)))
    retval = fillHistograms(events)

    return retval
    

def fillHistograms(eventinfo):

    # dphill... leading and subleading
    # dphilnu ... just mc
    # dphilmet1... leading + MET
    # dphilmet2... subleading + MET
    # etaj... both tags
    # detajj ... tags
    
    mwwrange = [500, 700, 900, 1100, 1300, 20000]

    dphill = []
    dphilnu = []
    dphilmet1 = []
    dphilmet2 = []
    etaj = []
    detajj = []

    for i in xrange(5):
        dphill.append(ROOT.TH1D('dphill_%d' % i, '#Delta #phi between charged leptons %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 32, 0, ROOT.TMath.Pi()))
        dphilnu.append(ROOT.TH1D('dphilnu_%d' % i, '#Delta #phi between charged lepton and neutrino %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 32, 0, ROOT.TMath.Pi()))
        dphilmet1.append(ROOT.TH1D('dphilmet1_%d' % i, '#Delta #phi between leading lepton and MET %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 32, 0, ROOT.TMath.Pi()))
        dphilmet2.append(ROOT.TH1D('dphilmet2_%d' % i, '#Delta #phi between subleading lepton and MET %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 32, 0, ROOT.TMath.Pi()))
        etaj.append(ROOT.TH1D('etaj_%d' % i, '#eta of the tagging jet %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 25, -5., 5.))
        detajj.append(ROOT.TH1D('detajj_%d' % i, '#Delta #eta between tagging jets %d < M_{WW} < %d' % (mwwrange[i], mwwrange[i+1]), 25, 0., 10.))

    dphill.append(ROOT.TH1D('dphill', '#Delta #phi between leptons', 32, 0, ROOT.TMath.Pi()))
    dphilnu.append(ROOT.TH1D('dphilnu', '#Delta #phi between charged lepton and neutrino', 32, 0, ROOT.TMath.Pi()))
    dphilmet1.append(ROOT.TH1D('dphilmet1', '#Delta #phi between leading lepton and MET', 32, 0, ROOT.TMath.Pi()))
    dphilmet2.append(ROOT.TH1D('dphilmet2', '#Delta #phi between subleading lepton and MET', 32, 0, ROOT.TMath.Pi()))
    etaj.append(ROOT.TH1D('etaj', '#eta of the tagging jet', 25, -5., 5.))
    detajj.append(ROOT.TH1D('detajj', '#Delta #eta between tagging jets', 25, 0., 10.))
    
    for event in eventinfo:
        lep = event[0]
        jet = event[1]
        nu = event[2]
        w = event[3]
        MET = reduce(lambda x,y:x+y, nu)
        wgt = event[4]
        index = [(w[0] + w[1]).M() > boundary for boundary in mwwrange].count(True)-1

        dphill_ = ROOT.TMath.Abs(ROOT.TVector2.Phi_mpi_pi(lep[0].DeltaPhi(lep[1])))
        dphilnu1_ = ROOT.TMath.Abs(ROOT.TVector2.Phi_mpi_pi(lep[0].DeltaPhi(nu[0])))
        dphilnu2_ = ROOT.TMath.Abs(ROOT.TVector2.Phi_mpi_pi(lep[1].DeltaPhi(nu[1])))
        lep.sort(key=lambda particle: particle.Pt(), reverse=True)
        jet.sort(key=lambda particle: particle.Pt(), reverse=True)
        dphilmet1_ = ROOT.TMath.Abs(ROOT.TVector2.Phi_mpi_pi(lep[0].DeltaPhi(MET)))
        dphilmet2_ = ROOT.TMath.Abs(ROOT.TVector2.Phi_mpi_pi(lep[1].DeltaPhi(MET)))
        etaj1_ = jet[0].Eta()
        etaj2_ = jet[1].Eta()
        detajj_ = ROOT.TMath.Abs(jet[0].Eta() - jet[1].Eta())

#        print dphill_, dphilnu1_, dphilnu2_, dphilmet1_, dphilmet2_, etaj1_, etaj2_, detajj_

        dphill[index].Fill(dphill_, wgt)
        dphill[-1].Fill(dphill_, wgt)
        
        dphilnu[index].Fill(dphilnu1_, wgt)
        dphilnu[-1].Fill(dphilnu1_, wgt)
        dphilnu[index].Fill(dphilnu2_, wgt)
        dphilnu[-1].Fill(dphilnu2_, wgt)

        dphilmet1[index].Fill(dphilmet1_, wgt)
        dphilmet1[-1].Fill(dphilmet1_, wgt)
        
        dphilmet2[index].Fill(dphilmet2_, wgt)
        dphilmet2[-1].Fill(dphilmet2_, wgt)
                
        etaj[index].Fill(etaj1_, wgt)
        etaj[-1].Fill(etaj1_, wgt)
        etaj[index].Fill(etaj2_, wgt)
        etaj[-1].Fill(etaj2_, wgt)

        detajj[index].Fill(detajj_, wgt)
        detajj[-1].Fill(detajj_, wgt)

    return [dphill, dphilnu, dphilmet1, dphilmet2, etaj, detajj]

def getEvents(LHEFile, numberOfRuns):

    ''' Reads LHE file and returns the weights and dependent variables '''

    retval = []

    print LHEFile
    try:
        tree = ET.parse(LHEFile)
        root = tree.getroot()
    except:
        return retval

    for child in root.findall('event'):

        # All the info I may ever want
        lep = []
        nu = []
        jet = []
        w = []
        
        asrwt = int(child.find('mgrwt').find('asrwt').text)
            
        eventInfo = child.text.splitlines()
        eventWeight = float(eventInfo[1].split()[2])/numberOfRuns
        
        for line in eventInfo[2:]:
            particleInfo = line.split()
            try:
                pdgID = int(particleInfo[0])
                isStable = int(particleInfo[1])
                px = float(particleInfo[6])
                py = float(particleInfo[7])
                pz = float(particleInfo[8])
                E = float(particleInfo[9])
            except:
                continue
            
            if ROOT.TMath.Abs(pdgID) == 11 or ROOT.TMath.Abs(pdgID) == 13 or ROOT.TMath.Abs(pdgID) == 15:
                lep.append(ROOT.TLorentzVector(px,py,pz,E))
            elif ROOT.TMath.Abs(pdgID) == 12 or ROOT.TMath.Abs(pdgID) == 14 or ROOT.TMath.Abs(pdgID) == 16:
                nu.append(ROOT.TLorentzVector(px,py,pz,E))
            elif ROOT.TMath.Abs(pdgID) == 24:
                w.append(ROOT.TLorentzVector(px,py,pz,E))
            elif isStable > 0:
                jet.append(ROOT.TLorentzVector(px,py,pz,E))

        passSelection = eventSelector(lep, jet, nu)
        
        if (passSelection):

            retval.append([lep, jet, nu, w, eventWeight])

    return retval

def eventSelector(lep, jet, nu):

    '''Event selection but mjj and detajj, that will be used as dependent variables for the cross section'''

    retval = 1.
    MET = reduce(lambda x,y:x+y, nu)

    # I know that I could write this in less lines, but I think it is more readable this way
    if lep[0].Pt() < 20. or lep[1].Pt() < 20.:
        retval = 0.
    if ROOT.TMath.Abs(lep[0].Eta()) > 2.5 or ROOT.TMath.Abs(lep[1].Eta()) > 2.5:
        retval = 0.

    if (lep[0]+lep[1]).M() < 45:
        retval = 0.

    if lep[0].Pt() < 30. or lep[1].Pt() < 30.:
        retval = 0.
    if ROOT.TMath.Abs(jet[0].Eta()) > 4.7 or ROOT.TMath.Abs(jet[1].Eta()) > 4.7:
        retval = 0.

    if (jet[0]+jet[1]).M() < 500:
        retval = 0.
    if ROOT.TMath.Abs(jet[0].Eta()-jet[1].Eta()) < 2.5:
        retval = 0.

    if MET.Pt() < 40.:
        retval = 0.

    return retval
    

        
if __name__ == "__main__":

    TTfiles = []
    for i in xrange(1, 501):
        if os.path.exists('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/TT/unweighted_events_%d.lhe' % i):
            TTfiles.append('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/TT/unweighted_events_%d.lhe' % i)
    TThists = readFiles(TTfiles)

    TLfiles = []
    for i in xrange(1, 501):        
        if os.path.exists('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/TL/unweighted_events_%d.lhe' % i):
            TLfiles.append('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/TL/unweighted_events_%d.lhe' % i)
    TLhists = readFiles(TLfiles)

    LLfiles = []
    for i in xrange(1, 501):        
        if os.path.exists('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/LL/unweighted_events_%d.lhe' % i):
            LLfiles.append('/eos/uscms/store/user/rclsa/Summer2014/LHEsource2/ssWW_2jets_To2L2Nu_madgraph/LL/unweighted_events_%d.lhe' % i)
    LLhists = readFiles(LLfiles)

    outputFile= ROOT.TFile('LHEevents.root', 'recreate')
    outputFile.mkdir('TT')
    outputFile.cd('TT')
    for hists in TThists:
        for hist in hists:
            hist.Write()

    outputFile.mkdir('TL')
    outputFile.cd('TL')
    for hists in TLhists:
        for hist in hists:
            hist.Write()

    outputFile.mkdir('LL')
    outputFile.cd('LL')
    for hists in LLhists:
        for hist in hists:
            hist.Write()

    outputFile.Close()
    
