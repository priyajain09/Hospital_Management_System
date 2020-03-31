import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// Import the components so they can be referenced in routes
import { CreateTreatmentComponent } from './treatment/create-treatment.component';
import { ListTreatmentsComponent } from './treatment/list-treatment.component';
import {HomeComponent} from './treatment/home.component';
// The last route is the empty path route. This specifies
// the route to redirect to if the client side path is empty.
const appRoutes: Routes = [
  { path: 'Show_treatments', component: ListTreatmentsComponent },
  { path: 'Create_treatment', component: CreateTreatmentComponent },
  { path: 'edit/:id', component: CreateTreatmentComponent },
  { path: 'Home', component: HomeComponent },
  { path: '', redirectTo: '/Home', pathMatch: 'full' }
];

// Pass the configured routes to the forRoot() method
// to let the angular router know about our routes
// Export the imported RouterModule so router directives
// are available to the module that imports this AppRoutingModule
@NgModule({
  imports: [ RouterModule.forRoot(appRoutes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule { }