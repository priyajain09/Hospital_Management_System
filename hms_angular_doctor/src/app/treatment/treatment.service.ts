import { Injectable } from '@angular/core';
import { ITreat } from './ITreat';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class TreatmentService {
    baseUrl = 'http://localhost:3000/treatment';
    constructor(private httpClient: HttpClient) {
    }

    getTreatments(): Observable<ITreat[]> {
        return this.httpClient.get<ITreat[]>(this.baseUrl)
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

    getTreatment(id: number): Observable<ITreat> {
        return this.httpClient.get<ITreat>(`${this.baseUrl}/${id}`)
            .pipe(catchError(this.handleError));
    }

    addTreatment(treatment: ITreat): Observable<ITreat> {
        return this.httpClient.post<ITreat>(this.baseUrl, treatment, {
            headers: new HttpHeaders({
                'Content-Type': 'application/json'
            })
        })
        .pipe(catchError(this.handleError));
    }

    updateTreatment(treatment: ITreat): Observable<void> {
        return this.httpClient.put<void>(`${this.baseUrl}/${treatment.id}`, treatment, {
            headers: new HttpHeaders({
                'Content-Type': 'application/json'
            })
        })
            .pipe(catchError(this.handleError));
    }

    deleteTreatment(id: number): Observable<void> {
        return this.httpClient.delete<void>(`${this.baseUrl}/${id}`)
            .pipe(catchError(this.handleError));
    }
}