{
//TBrowser *b=new TBrowser;
double ndata=data->Integral();
TH1F *bg = new TH1F("bg","bg",50,0,0.11); 
// bg->Sumw2();
 bg->Add(wj,st,0.54,0.46);
 TH1F *ttg = new TH1F("ttg","ttg",50,0,0.11); 
// ttg->Sumw2();
 ttg->Add(ttgg,ttqq,0.87,0.13);
TH1F *ttq = new TH1F("ttq","ttq",50,0,0.11); 
// ttq->Sumw2();
 ttq->Add(ttqg,ttag,0.84,0.16);
TH1F *bg1 = new TH1F("bg1","bg1",50,0,0.11); 
 bg1->Add(wj,st,0.54,0.46);
TH1F *ttg1 = new TH1F("ttg1","ttg1",50,0,0.11); 
 ttg1->Add(ttgg,ttqq,0.87,0.13);
TH1F *ttq1 = new TH1F("ttq1","ttq1",50,0,0.11); 
 ttq1->Add(ttqg,ttag,0.84,0.16);
int nbins=50;
//for(int i=0; i<nbins; i++)
//{
//  double e=0.0001;
//  bg->SetBinError(i,e);
//  bg1->SetBinError(i,e);
//  ttg->SetBinError(i,e);
//  ttg1->SetBinError(i,e);
//  ttq->SetBinError(i,e);
//  ttq1->SetBinError(i,e);
//}


TObjArray *mc80=new TObjArray(3);
mc80->Add(bg);
mc80->Add(ttg);
mc80->Add(ttq);
TFractionFitter *fit0=new TFractionFitter(data,mc80);
fit0->Constrain(1,0.095,0.105);
fit0->Constrain(2,0.0,0.9);
fit0->Constrain(3,0.0,0.9);
Int_t status=fit0->Fit();
TCanvas *c0=new TCanvas("c0","ttj fit",600,400);
if (status==0) {
  //TH1 *tt0=(TH1*) fit0->GetMCPrediction(0);
  TH1 *result0=(TH1F*) fit0->GetPlot();
  data->Draw("Ep");
//  result0->Draw("same");
  //tt0.SetLineColor(4);
  //tt0->Draw("same"); 
}
double fbg;
double dfbg;
fit0->GetResult(0,fbg,dfbg);
double scale=ndata*fbg;
bg1->Scale(scale);

double fttg;
double dfttg;
fit0->GetResult(1,fttg,dfttg);
double scale=ndata*fttg;
ttg1->Scale(scale);
TH1F *sm1 = new TH1F("sm1","sm1",50,0,0.11); 
 sm1->Add(bg1,ttg1,1.,1.);

double fttq;
double dfttq;
fit0->GetResult(2,fttq,dfttq);
double scale=ndata*fttq;
ttq1->Scale(scale);
TH1F *sm2 = new TH1F("sm2","sm2",50,0,0.11); 
 sm2->Add(sm1,ttq1,1.,1.);
 sm2->SetLineColor(kRed);
 sm2->Draw("same");
 sm1->SetLineColor(kBlue+2);
 sm1->Draw("same");
 bg1->SetLineColor(kRed-7);
 bg1->Draw("same");

cout << "fttg from Lhood=" << fttg << " +-" << dfttg<<  "\n";
cout << "fttq from Lhood=" << fttq << " +-" << dfttq<<  "\n";


}



