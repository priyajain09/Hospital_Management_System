import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { CreateTreatmentComponent } from './treatment/create-treatment.component';
import { ListTreatmentsComponent } from './treatment/list-treatment.component';
import { AppRoutingModule } from './app-routing.module';
import { TreatmentService } from './treatment/treatment.service';
import { HttpClientModule } from '@angular/common/http';
import { HomeComponent } from './treatment/home.component';
import { HomeService } from './treatment/home.service';
@NgModule({
  declarations: [
    AppComponent,
    CreateTreatmentComponent,
    ListTreatmentsComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule
  ],

  providers: [TreatmentService, HomeService],
  bootstrap: [AppComponent]
})
export class AppModule { }
