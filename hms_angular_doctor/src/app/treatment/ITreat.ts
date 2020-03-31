import { IAllDoct } from './IAllDoct';
import { IPresc } from './IPresc';

export interface ITreat {
    id: number;
    patient_userid: string;
    patient_name: string;
    start_date: string;
    time_stamp: string;
    Referto: string;
    alldoctors: IAllDoct[];
    prescription : IPresc[];
}
