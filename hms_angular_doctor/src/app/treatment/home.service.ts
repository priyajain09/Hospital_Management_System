import { Injectable } from '@angular/core';
import { IDoctor } from './IDoctor';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class HomeService {
    baseUrl = 'http://localhost:3000/doctor';
    constructor(private httpClient: HttpClient) {
    }

    getDoctors(): Observable<IDoctor[]> {
        return this.httpClient.get<IDoctor[]>(this.baseUrl)
            .pipe(catchError(this.handleError));
    }

    private handleError(errorResponse: HttpErrorResponse) {
        if (errorResponse.error instanceof ErrorEvent) {
            console.error('Client Side Error :', errorResponse.error.message);
        } else {
            console.error('Server Side Error :', errorResponse);
        }
        return throwError('There is a problem with the service. We are notified & working on it. Please try again later.');
    }

    getDoctor(id: number): Observable<IDoctor> {
        return this.httpClient.get<IDoctor>(`${this.baseUrl}/${id}`)
            .pipe(catchError(this.handleError));
    }

    updateTreatment(doctor: IDoctor): Observable<void> {
        return this.httpClient.put<void>(`${this.baseUrl}/${doctor.id}`, doctor, {
            headers: new HttpHeaders({
                'Content-Type': 'application/json'
            })
        })
            .pipe(catchError(this.handleError));
    }
}